from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from utilities.keycloak_authentication import keycloak_token_required
from utilities.security_utils import InputValidator, validate_file_upload, rate_limit_decorator
from classes.prescription import Prescription_Methods
from utilities.security_utils import InputValidator, validate_file_upload, rate_limit_decorator

prescriptions_bp = Blueprint('prescriptions', __name__)

UPLOAD_FOLDER = 'prescriptions'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@prescriptions_bp.route('/prescriptions', methods=['GET'])
@keycloak_token_required
def get_all_prescriptions(user_id, roles):
    success, result = Prescription_Methods.findAllPrescriptions(user_id)
    if success:
        return jsonify(result), 200
    return jsonify({'error': result}), 404

@prescriptions_bp.route('/prescriptions', methods=['POST'])
@keycloak_token_required
@validate_file_upload
@rate_limit_decorator(max_requests=10, per_seconds=60)  
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
        if not InputValidator.validate_name(data['first_name']):
            return jsonify({'error': 'Invalid first name format'}), 400
        
        if not InputValidator.validate_name(data['last_name']):
            return jsonify({'error': 'Invalid last name format'}), 400
        
        if not InputValidator.validate_pesel(data['pesel']):
            return jsonify({'error': 'Invalid PESEL number'}), 400
        first_name = InputValidator.sanitize_string(data['first_name'])
        last_name = InputValidator.sanitize_string(data['last_name'])
        pesel = data['pesel']  
        med_info = InputValidator.sanitize_string(data.get('med_info_for_search', ''))
        if not current_app.minio_handler:
            return jsonify({'error': 'File storage service is currently unavailable'}), 503

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
            first_name,
            last_name,
            pesel,
            data['issue_date'],
            data['expiry_date'],
            file_url,
            med_info
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
        print(f"Error in add_prescription_no_pdf: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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

        if prescription[0] and current_app.minio_handler:
            file_path = '/'.join(prescription[0].split('/')[-3:])
            current_app.minio_handler.delete_file(file_path)
        elif prescription[0] and not current_app.minio_handler:
            current_app.logger.warning(f"Cannot delete file {prescription[0]} - MinIO unavailable")

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

@prescriptions_bp.route('/prescriptions/search/person', methods=['GET'])
@keycloak_token_required
def find_by_person(user_id, roles):
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not first_name or not last_name:
        return jsonify({'error': 'First name and last name are required'}), 400
        
    success, result = Prescription_Methods.findPrescriptionsByPerson(
        user_id, first_name, last_name, start_date, end_date
    )
    if success:
        return jsonify(result), 200
    return jsonify({'error': result}), 404

@prescriptions_bp.route('/prescriptions/search/medication', methods=['GET'])
@keycloak_token_required
def find_by_medication(user_id, roles):
    med_pattern = request.args.get('medication')
    if not med_pattern:
        return jsonify({'error': 'Medication pattern is required'}), 400
        
    success, result = Prescription_Methods.findByMedication(user_id, med_pattern)
    if success:
        return jsonify(result), 200
    return jsonify({'error': result}), 404

@prescriptions_bp.route('/prescriptions/person', methods=['DELETE'])
@keycloak_token_required
def delete_by_name(user_id, roles):
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    if not first_name or not last_name:
        return jsonify({'error': 'First name and last name are required'}), 400
        
    success, message = Prescription_Methods.DeleteByName(user_id, first_name, last_name)
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), 400

@prescriptions_bp.route('/prescriptions/expired', methods=['DELETE'])
@keycloak_token_required
def delete_expired(user_id, roles):
    before_date = request.args.get('before_date')
    success, message = Prescription_Methods.deletePrescriptionsByDate(user_id, before_date)
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), 400
