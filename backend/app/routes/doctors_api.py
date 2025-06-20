from flask import Blueprint, request, jsonify, current_app
from utilities.keycloak_authentication import keycloak_token_required

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('/doctors', methods=['POST'])
@keycloak_token_required
def add_doctor_info(user_id, roles):
    try:
        data = request.get_json()
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM doctors 
            WHERE user_id = %s
        """, (user_id,))

        if cur.fetchone():
            return jsonify({
                'error': 'Doctor info already exists. Use PUT to update.'
            }), 409

        cur.execute("""
            INSERT INTO doctors (first_name, last_name, user_id)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (data['first_name'], data['last_name'], user_id))

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
@keycloak_token_required
def get_doctor_info(user_id, roles):
    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, first_name, last_name
            FROM doctors
            WHERE user_id = %s
        """, (user_id,))

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
@keycloak_token_required
def update_doctor_info(user_id, roles):
    try:
        data = request.get_json()
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE doctors
            SET first_name = %s, last_name = %s
            WHERE user_id = %s
            RETURNING id
        """, (data['first_name'], data['last_name'], user_id))

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
@keycloak_token_required
def delete_doctor_info(user_id, roles):
    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM doctors
            WHERE user_id = %s
            RETURNING id
        """, (user_id,))

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
