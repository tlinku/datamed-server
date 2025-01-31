# notes_api.py
from flask import Blueprint, request, jsonify, current_app
from utilities.jwt_authentication import token_required
import json

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/notes', methods=['POST'])
@token_required
def add_note(current_user_id):
    try:
        data = request.get_json()
        note_content = {
            'name': data['name'],
            'content': data['content']
        }
        
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO notes (user_id, note_name)
            VALUES (%s, %s)
            RETURNING id
        """, (current_user_id, json.dumps(note_content)))
        
        note_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({'id': note_id}), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@notes_bp.route('/notes', methods=['GET'])
@token_required
def get_all_notes(current_user_id):
    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, note_name
            FROM notes
            WHERE user_id = %s
        """, (current_user_id,))
        
        notes = cur.fetchall()
        return jsonify([{
            'id': note[0],
            'note': note[1]
        } for note in notes]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@notes_bp.route('/notes/<int:note_id>', methods=['PUT'])
@token_required
def update_note(current_user_id, note_id):
    try:
        data = request.get_json()
        note_content = {
            'name': data['name'],
            'content': data['content']
        }
        
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE notes
            SET note_name = %s
            WHERE id = %s AND user_id = %s
            RETURNING id
        """, (json.dumps(note_content), note_id, current_user_id))
        
        if cur.fetchone() is None:
            return jsonify({'error': 'Note not found'}), 404
            
        conn.commit()
        return jsonify({'message': 'Note updated successfully'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@notes_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@token_required
def delete_note(current_user_id, note_id):
    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            DELETE FROM notes
            WHERE id = %s AND user_id = %s
            RETURNING id
        """, (note_id, current_user_id))
        
        if cur.fetchone() is None:
            return jsonify({'error': 'Note not found'}), 404
            
        conn.commit()
        return jsonify({'message': 'Note deleted successfully'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)

@notes_bp.route('/notes', methods=['DELETE'])
@token_required
def delete_all_notes(current_user_id):
    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            DELETE FROM notes
            WHERE user_id = %s
            RETURNING id
        """, (current_user_id,))
        
        deleted = cur.fetchall()
        conn.commit()
        return jsonify({
            'message': 'All notes deleted successfully',
            'count': len(deleted)
        }), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)
@notes_bp.route('/notes/<int:note_id>', methods=['GET'])
@token_required
def get_note(current_user_id, note_id):
    try:
        conn = current_app.db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, note_name
            FROM notes
            WHERE id = %s AND user_id = %s
        """, (note_id, current_user_id))
        
        note = cur.fetchone()
        if not note:
            return jsonify({'error': 'Note not found'}), 404
            
        return jsonify({
            'id': note[0],
            'note': note[1]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            current_app.db_pool.putconn(conn)