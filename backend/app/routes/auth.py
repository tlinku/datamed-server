from flask import Blueprint, request, jsonify, current_app
from utilities.authentication import Authentication
from werkzeug.security import check_password_hash
from utilities.jwt_authentication import create_token
from utilities.keycloak_authentication import create_keycloak_user, delete_keycloak_user, find_keycloak_user_by_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    conn = None
    cur = None
    keycloak_user_id = None

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400

    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()        
        cur.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        if cur.fetchone():
            return jsonify({'error': 'Email already exists'}), 400
        try:
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            keycloak_user_id = create_keycloak_user(
                data['email'], 
                data['password'],
                first_name,
                last_name
            )
            print(f"Created user in Keycloak with ID: {keycloak_user_id}")
        except Exception as ke:
            print(f"Failed to create user in Keycloak: {str(ke)}")
            return jsonify({'error': f'Failed to create user in authentication system: {str(ke)}'}), 500
        user_data = Authentication.create_account(data['email'], data['password'])
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
            (user_data['email'], user_data['password_hash'])
        )
        user_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({
            'message': 'Account created successfully in both systems',
            'user_id': user_id,
            'keycloak_user_id': keycloak_user_id
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        if keycloak_user_id:
            try:
                delete_keycloak_user(keycloak_user_id)
                print(f"Deleted Keycloak user {keycloak_user_id} after database error")
            except Exception as ke:
                print(f"Failed to delete Keycloak user after error: {str(ke)}")

        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = None
    cur = None

    try:
        print("Received login request:", data)

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400

        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        print("Connected to database")

        cur.execute(
            "SELECT id, email, password_hash FROM users WHERE email = %s",
            (data['email'],)
        )
        user = cur.fetchone()

        print("User found:", user)

        if not user or not check_password_hash(user[2], data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401

        if 'TOKEN_KEY' not in current_app.config:
            raise ValueError("TOKEN_KEY not configured")


        return jsonify({
            'message': 'Login successful',
            'user_id': user[0],
            'email': user[1],
            'token': create_token(user[0])
        }), 200

    except Exception as e:
        print("Error in login:", str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@auth_bp.route('/auth/password', methods=['PUT'])
def update_password_via_site():
    data = request.get_json()
    conn = None
    cur = None

    if not data or not data.get('email') or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, password_hash FROM users WHERE email = %s",
            (data['email'],)
        )
        user = cur.fetchone()

        if not user or not check_password_hash(user[1], data['old_password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        new_password_hash = Authentication.hash_password(data['new_password'])
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_password_hash, user[0])
        )
        conn.commit()

        return jsonify({'message': 'Password updated successfully'}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
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
