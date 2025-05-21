from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from utilities.keycloak_authentication import keycloak_token_required

prescriptions_bp = Blueprint('prescriptions', __name__)

UPLOAD_FOLDER = 'prescriptions'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@prescriptions_bp.route('/prescriptions', methods=['POST'])
@keycloak_token_required
def add_prescription(user_id, roles):
    conn = None
    cur = None

    try:
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['pdf_file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400

        data = request.form
        required_keys = ['first_name', 'last_name', 'pesel', 'issue_date', 'expiry_date']
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_keys)}'}), 400

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{user_id}_{timestamp}_{file.filename}")
        file_path = f"prescriptions/{user_id}/{filename}"
        file_url = current_app.minio_handler.upload_file(
            file_path,
            file.read(),
            content_type="application/pdf"
        )

        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO prescriptions 
            (user_id, first_name, last_name, pesel, issue_date, expiry_date, pdf_url, med_info_for_search)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_id,
            data['first_name'],
            data['last_name'],
            data['pesel'],
            data['issue_date'],
            data['expiry_date'],
            file_url,
            data.get('med_info_for_search', '')
        ))

        prescription_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({
            'message': 'Prescription added successfully',
            'prescription_id': prescription_id,
            'pdf_url': file_url
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)
@prescriptions_bp.route('/prescriptions/no-pdf', methods=['POST'])
@keycloak_token_required
def add_prescription_no_pdf(user_id, roles):
    conn = None
    cur = None

    try:
        data = request.get_json()
        if not all(key in data for key in ['first_name', 'last_name', 'pesel', 'issue_date', 'expiry_date']):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO prescriptions 
            (user_id, first_name, last_name, pesel, issue_date, expiry_date, med_info_for_search)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_id,
            data['first_name'],
            data['last_name'],
            data['pesel'],
            data['issue_date'],
            data['expiry_date'],
            data.get('med_info_for_search', '')
        ))
        prescription_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({
            'message': 'Prescription added successfully',
            'prescription_id': prescription_id
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@prescriptions_bp.route('/prescriptions/<int:prescription_id>', methods=['GET'])
@keycloak_token_required
def get_prescription(user_id, roles, prescription_id):
    conn = None
    cur = None

    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM prescriptions 
            WHERE id = %s AND user_id = %s
        """, (prescription_id, user_id))

        prescription = cur.fetchone()
        if not prescription:
            return jsonify({'error': 'Prescription not found'}), 404

        columns = ['id', 'user_id', 'first_name', 'last_name', 'pesel', 
                  'issue_date', 'expiry_date', 'pdf_url', 'med_info_for_search']
        prescription_dict = dict(zip(columns, prescription))

        return jsonify(prescription_dict), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@prescriptions_bp.route('/prescriptions/<int:prescription_id>', methods=['DELETE'])
@keycloak_token_required
def delete_prescription(user_id, roles, prescription_id):
    conn = None
    cur = None

    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            SELECT pdf_url FROM prescriptions 
            WHERE id = %s AND user_id = %s
        """, (prescription_id, user_id))

        prescription = cur.fetchone()
        if not prescription:
            return jsonify({'error': 'Prescription not found'}), 404

        if prescription[0]:
            # Extract file path from URL
            file_path = '/'.join(prescription[0].split('/')[-3:])
            # Use MinIO for file deletion
            current_app.minio_handler.delete_file(file_path)

        cur.execute("""
            DELETE FROM prescriptions 
            WHERE id = %s AND user_id = %s
        """, (prescription_id, user_id))

        conn.commit()
        return jsonify({'message': 'Prescription deleted successfully'}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)
