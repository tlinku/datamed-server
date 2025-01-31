from flask import Blueprint, request, jsonify, current_app
from utilities.jwt_authentication import token_required

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('/doctors', methods=['POST'])
@token_required
def add_doctor_info(current_user_id):
    try:
        data = request.get_json()
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM doctors_info 
            WHERE user_id = %s
        """, (current_user_id,))
        
        if cur.fetchone():
            return jsonify({
                'error': 'Doctor info already exists. Use PUT to update.'
            }), 409
        
        cur.execute("""
            INSERT INTO doctors_info (first_name, last_name, user_id)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (data['first_name'], data['last_name'], current_user_id))
        
        doctor_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({'id': doctor_id}), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@doctors_bp.route('/doctors', methods=['GET'])
@token_required
def get_doctor_info(current_user_id):
    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, first_name, last_name
            FROM doctors_info
            WHERE user_id = %s
        """, (current_user_id,))
        
        doctor = cur.fetchone()
        if not doctor:
            return jsonify({'error': 'Doctor info not found'}), 404
            
        return jsonify({
            'id': doctor[0],
            'first_name': doctor[1],
            'last_name': doctor[2]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@doctors_bp.route('/doctors', methods=['PUT'])
@token_required
def update_doctor_info(current_user_id):
    try:
        data = request.get_json()
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE doctors_info
            SET first_name = %s, last_name = %s
            WHERE user_id = %s
            RETURNING id
        """, (data['first_name'], data['last_name'], current_user_id))
        
        if cur.fetchone() is None:
            return jsonify({'error': 'Doctor info not found'}), 404
            
        conn.commit()
        return jsonify({'message': 'Doctor info updated successfully'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@doctors_bp.route('/doctors', methods=['DELETE'])
@token_required
def delete_doctor_info(current_user_id):
    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            DELETE FROM doctors_info
            WHERE user_id = %s
            RETURNING id
        """, (current_user_id,))
        
        if cur.fetchone() is None:
            return jsonify({'error': 'Doctor info not found'}), 404
            
        conn.commit()
        return jsonify({'message': 'Doctor info deleted successfully'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)