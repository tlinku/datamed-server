from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime
from classes.prescription  import Prescription_Methods

prescription_routes = Blueprint('prescription_routes', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, current_app.config['TOKEN_KEY'], algorithms=["HS256"])
            user_id = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(user_id, *args, **kwargs)
    return decorated

@prescription_routes.route('/prescriptions', methods=['GET'])
@token_required
def get_all_prescriptions(user_id):
    success, result = Prescription_Methods.findAllPrescriptions(user_id)
    if success:
        return jsonify(result), 200
    return jsonify({'error': result}), 404

@prescription_routes.route('/prescriptions/search/person', methods=['GET'])
@token_required
def find_by_person(user_id):
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

@prescription_routes.route('/prescriptions/search/medication', methods=['GET'])
@token_required
def find_by_medication(user_id):
    med_pattern = request.args.get('medication')
    if not med_pattern:
        return jsonify({'error': 'Medication pattern is required'}), 400
        
    success, result = Prescription_Methods.findByMedication(user_id, med_pattern)
    if success:
        return jsonify(result), 200
    return jsonify({'error': result}), 404

@prescription_routes.route('/prescriptions/person', methods=['DELETE'])
@token_required
def delete_by_name(user_id):
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    if not first_name or not last_name:
        return jsonify({'error': 'First name and last name are required'}), 400
        
    success, message = Prescription_Methods.DeleteByName(user_id, first_name, last_name)
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), 400

@prescription_routes.route('/prescriptions/expired', methods=['DELETE'])
@token_required
def delete_expired(user_id):
    before_date = request.args.get('before_date')
    success, message = Prescription_Methods.deletePrescriptionsByDate(user_id, before_date)
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), 400