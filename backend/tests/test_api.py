# test_apis.py
import pytest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from run import app
from datetime import datetime

TEST_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE3Mzg0Mzg1MDJ9.VxxXHztnVVuU9IyM6XeQJBDN9O5BN9abPaArzZm04do"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    return {
        'Authorization': f'Bearer {TEST_TOKEN}',
        'Content-Type': 'application/json'
    }

def test_doctor_crud(client, auth_headers):
    create_response = client.post('/doctors', 
        headers=auth_headers,
        json={
            'first_name': 'John',
            'last_name': 'Doe'
        }
    )
    assert create_response.status_code == 201
    assert 'id' in create_response.json

    duplicate_response = client.post('/doctors',
        headers=auth_headers,
        json={
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
    )
    assert duplicate_response.status_code == 409

    get_response = client.get('/doctors', headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json['first_name'] == 'John'
    assert get_response.json['last_name'] == 'Doe'

    update_response = client.put('/doctors',
        headers=auth_headers,
        json={
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
    )
    assert update_response.status_code == 200

    get_updated = client.get('/doctors', headers=auth_headers)
    assert get_updated.json['first_name'] == 'Jane'
    assert get_updated.json['last_name'] == 'Smith'

    delete_response = client.delete('/doctors', headers=auth_headers)
    assert delete_response.status_code == 200

    get_deleted = client.get('/doctors', headers=auth_headers)
    assert get_deleted.status_code == 404

def test_notes_crud(client, auth_headers):
    create_response = client.post('/notes',
        headers=auth_headers,
        json={
            'name': 'Test Note',
            'content': 'Test Content'
        }
    )
    assert create_response.status_code == 201
    note_id = create_response.json['id']

    get_response = client.get('/notes', headers=auth_headers)
    assert get_response.status_code == 200
    assert len(get_response.json) > 0
    assert any(note['note']['name'] == 'Test Note' for note in get_response.json)

    update_response = client.put(f'/notes/{note_id}',
        headers=auth_headers,
        json={
            'name': 'Updated Note',
            'content': 'Updated Content'
        }
    )
    assert update_response.status_code == 200

    delete_response = client.delete(f'/notes/{note_id}', headers=auth_headers)
    assert delete_response.status_code == 200

def test_notes_bulk_operations(client, auth_headers):
    notes = [
        {'name': f'Note {i}', 'content': f'Content {i}'} 
        for i in range(3)
    ]
    
    for note in notes:
        response = client.post('/notes',
            headers=auth_headers,
            json=note
        )
        assert response.status_code == 201

    get_response = client.get('/notes', headers=auth_headers)
    assert get_response.status_code == 200
    assert len(get_response.json) >= 3

    delete_all_response = client.delete('/notes', headers=auth_headers)
    assert delete_all_response.status_code == 200
    assert delete_all_response.json['count'] >= 3

    get_empty = client.get('/notes', headers=auth_headers)
    assert get_empty.status_code == 200
    assert len(get_empty.json) == 0

def test_error_cases(client, auth_headers):
    get_response = client.get('/notes/99999', headers=auth_headers)
    assert get_response.status_code == 404

    update_response = client.put('/notes/99999',
        headers=auth_headers,
        json={
            'name': 'Test',
            'content': 'Test'
        }
    )
    assert update_response.status_code == 404

    delete_response = client.delete('/notes/99999', headers=auth_headers)
    assert delete_response.status_code == 404

    invalid_response = client.post('/notes',
        headers=auth_headers,
        json={
            'name': 'Test'
        }
    )
    assert invalid_response.status_code == 401