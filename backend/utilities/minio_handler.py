from minio import Minio
from minio.error import S3Error
import os
from flask import current_app
import io
from datetime import timedelta

class MinioHandler:
    def __init__(self, app=None):
        self.client = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        try:
            minio_url = os.getenv('MINIO_URL', 'http://minio:9000').replace('http://', '')
            
            # Try to read from K8s secret mount first, then fall back to environment variables
            minio_access_key_path = '/run/secrets/app/MINIO_ACCESS_KEY'
            minio_secret_key_path = '/run/secrets/app/MINIO_SECRET_KEY'
            
            if os.path.exists(minio_access_key_path):
                with open(minio_access_key_path, 'r') as f:
                    minio_access_key = f.read().strip()
                app.logger.info("MinIO access key loaded from secret mount")
            else:
                minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
                app.logger.info("MinIO access key loaded from environment")
                
            if os.path.exists(minio_secret_key_path):
                with open(minio_secret_key_path, 'r') as f:
                    minio_secret_key = f.read().strip()
                app.logger.info("MinIO secret key loaded from secret mount")
            else:
                minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
                app.logger.info("MinIO secret key loaded from environment")
                
            self.bucket_name = os.getenv('MINIO_BUCKET', 'prescriptions')

            app.logger.info(f"Initializing MinIO with URL: {minio_url}, Bucket: {self.bucket_name}")

            self.client = Minio(
                minio_url,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=False
            )
            
            # Test connection with timeout
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("MinIO connection timeout")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)  # 10 second timeout
            
            try:
                buckets = list(self.client.list_buckets())
                app.logger.info(f"MinIO connection successful. Found {len(buckets)} buckets")
                if not self.client.bucket_exists(self.bucket_name):
                    self.client.make_bucket(self.bucket_name)
                    app.logger.info(f"Created bucket: {self.bucket_name}")
                else:
                    app.logger.info(f"Bucket {self.bucket_name} already exists")
            finally:
                signal.alarm(0)  # Disable alarm
                
        except Exception as e:
            app.logger.error(f"MinIO initialization failed: {e}")
            raise e
                
        except S3Error as e:
            if e.code == 'AccessDenied':
                app.logger.error(f"MinIO Access Denied - Check credentials and permissions. Error: {e}")
            else:
                app.logger.error(f"MinIO S3 Error: {e}")
            raise
        except Exception as e:
            app.logger.error(f"MinIO connection failed: {e}")
            raise

    def upload_file(self, file_path, file_data, content_type=None):
        try:
            if hasattr(file_data, 'read'):
                file_data = file_data.read()
            self.client.put_object(
                self.bucket_name,
                file_path,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type
            )
            url = self.client.presigned_get_object(
                self.bucket_name,
                file_path,
                expires=timedelta(days=7)  
            )
            
            return url
        except S3Error as e:
            current_app.logger.error(f"Error uploading file: {e}")
            raise

    def delete_file(self, file_path):
        try:
            self.client.remove_object(self.bucket_name, file_path)
            return True
        except S3Error as e:
            current_app.logger.error(f"Error deleting file: {e}")
            return False