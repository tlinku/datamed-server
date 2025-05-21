from minio import Minio
from minio.error import S3Error
import os
from flask import current_app
import io

class MinioHandler:
    def __init__(self, app=None):
        self.client = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        minio_url = os.getenv('MINIO_URL', 'http://minio:9000').replace('http://', '')
        minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        self.bucket_name = os.getenv('MINIO_BUCKET', 'prescriptions')

        self.client = Minio(
            minio_url,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False
        )
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                app.logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            app.logger.error(f"Error creating bucket: {e}")
            raise

    def upload_file(self, file_path, file_data, content_type=None):
        """
        Upload a file to MinIO
        
        Args:
            file_path (str): The path where the file will be stored
            file_data (bytes or file-like object): The file data to upload
            content_type (str, optional): The content type of the file
            
        Returns:
            str: The URL of the uploaded file
        """
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
                expires=7*24*60*60  
            )
            
            return url
        except S3Error as e:
            current_app.logger.error(f"Error uploading file: {e}")
            raise

    def delete_file(self, file_path):
        """
        Delete a file from MinIO
        
        Args:
            file_path (str): The path of the file to delete
            
        Returns:
            bool: True if the file was deleted, False otherwise
        """
        try:
            self.client.remove_object(self.bucket_name, file_path)
            return True
        except S3Error as e:
            current_app.logger.error(f"Error deleting file: {e}")
            return False