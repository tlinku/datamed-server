from flask import Blueprint, request, jsonify, current_app
from utilities.authentication import Authentication
from werkzeug.security import check_password_hash
from utilities.keycloak_authentication import delete_keycloak_user, find_keycloak_user_by_email, keycloak_token_required
from utilities.security_utils import InputValidator, rate_limit_decorator

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/password', methods=['PUT'])
@rate_limit_decorator(max_requests=5, per_seconds=300)  # 5 attempts per 5 minutes
@keycloak_token_required
def update_password_via_site(user_id, roles):
    data = request.get_json()
    conn = None
    cur = None

    if not data or not data.get('email') or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing required fields'}), 400
    if not InputValidator.validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    is_valid, message = InputValidator.validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    email = InputValidator.sanitize_string(data['email'])
    old_password = data['old_password']
    new_password = data['new_password']

    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM users WHERE email = %s AND id = %s",
            (email, user_id)
        )
        user = cur.fetchone()

        if not user or not check_password_hash(user[1], old_password):
            return jsonify({'error': 'Invalid credentials'}), 401

        new_password_hash = Authentication.hash_password(new_password)
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_password_hash, user[0])
        )
        conn.commit()

        return jsonify({'message': 'Password updated successfully'}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)
@auth_bp.route('/auth/account', methods=['DELETE'])
def delete_account():
    data = request.get_json()
    conn = None
    cur = None

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing credentials'}), 400

    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, password_hash, email FROM users WHERE email = %s",
            (data['email'],)
        )
        user = cur.fetchone()

        if not user or not check_password_hash(user[1], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401


        try:

            keycloak_user_id = find_keycloak_user_by_email(user[2])
            if keycloak_user_id:
                delete_result = delete_keycloak_user(keycloak_user_id)
                if delete_result:
                    print(f"Successfully deleted user from Keycloak with ID: {keycloak_user_id}")
                else:
                    print(f"Failed to delete user from Keycloak with ID: {keycloak_user_id}")
            else:
                print(f"No Keycloak user found with email: {user[2]}")
        except Exception as ke:
            print(f"Error deleting user from Keycloak: {str(ke)}")
        cur.execute(
            "DELETE FROM prescriptions WHERE user_id = %s",
            (user[0],)
        )

        cur.execute(
            "DELETE FROM users WHERE id = %s",
            (user[0],)
        )
        conn.commit()

        return jsonify({'message': 'Account deleted successfully'}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)
@auth_bp.route('/auth/logout', methods=['POST'])
@keycloak_token_required
def logout(user_id, roles):
    try:
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
