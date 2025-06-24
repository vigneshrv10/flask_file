import pytest
import os
import io
from app import app, db, bcrypt
from models import User, File

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['UPLOAD_FOLDER'] = 'test_uploads'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test uploads folder
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            yield client
            # Cleanup
            db.session.remove()
            db.drop_all()
            # Remove test uploads folder
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                for file in os.listdir(app.config['UPLOAD_FOLDER']):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
                os.rmdir(app.config['UPLOAD_FOLDER'])

def create_ops_user():
    hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
    user = User(email='ops@example.com', password=hashed_password, role='ops')
    db.session.add(user)
    db.session.commit()
    return user

def create_client_user(verified=True):
    hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
    user = User(
        email='client@example.com',
        password=hashed_password,
        role='client',
        is_verified=verified
    )
    db.session.add(user)
    db.session.commit()
    return user

def test_ops_login(client):
    create_ops_user()
    response = client.post('/api/ops/login', json={
        'email': 'ops@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_ops_login_invalid_credentials(client):
    create_ops_user()
    response = client.post('/api/ops/login', json={
        'email': 'ops@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_client_signup(client):
    response = client.post('/api/client/signup', json={
        'email': 'newclient@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    user = User.query.filter_by(email='newclient@example.com').first()
    assert user is not None
    assert user.role == 'client'
    assert not user.is_verified

def test_client_login_unverified(client):
    create_client_user(verified=False)
    response = client.post('/api/client/login', json={
        'email': 'client@example.com',
        'password': 'password123'
    })
    assert response.status_code == 403

def test_client_login_verified(client):
    create_client_user(verified=True)
    response = client.post('/api/client/login', json={
        'email': 'client@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_file_upload(client):
    # Create ops user and get token
    user = create_ops_user()
    login_response = client.post('/api/ops/login', json={
        'email': 'ops@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']
    
    # Create test file
    data = {}
    data['file'] = (io.BytesIO(b"test content"), "test.docx")
    
    response = client.post(
        '/api/ops/upload',
        data=data,
        headers={'Authorization': f'Bearer {token}'},
        content_type='multipart/form-data'
    )
    assert response.status_code == 201
    
    # Check if file was saved in database
    file = File.query.first()
    assert file is not None
    assert file.file_type == 'docx'
    assert file.uploaded_by == user.id

def test_list_files(client):
    # Create client user and get token
    user = create_client_user()
    login_response = client.post('/api/client/login', json={
        'email': 'client@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']
    
    response = client.get(
        '/api/client/files',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert 'files' in response.json

def test_get_download_link(client):
    # Create client user and get token
    user = create_client_user()
    login_response = client.post('/api/client/login', json={
        'email': 'client@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']
    
    # Create a test file in the database
    ops_user = create_ops_user()
    test_file = File(
        filename='test.docx',
        original_filename='test.docx',
        file_type='docx',
        uploaded_by=ops_user.id,
        download_token='test-token'
    )
    db.session.add(test_file)
    db.session.commit()
    
    response = client.get(
        f'/api/client/download/{test_file.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert 'download_link' in response.json
    assert 'message' in response.json
    assert response.json['message'] == 'success' 