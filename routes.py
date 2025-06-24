from flask import request, jsonify, send_from_directory, url_for, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message
from werkzeug.utils import secure_filename
import os
import uuid
from cryptography.fernet import Fernet
import mimetypes

from app import app, db, mail, bcrypt
from models import User, File

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pptx', 'docx', 'xlsx'}

# Generate encryption key for Fernet
encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_verification_email(user_email, token):
    msg = Message('Email Verification',
                 sender=app.config['MAIL_USERNAME'],
                 recipients=[user_email])
    verification_url = url_for('verify_email', token=token, _external=True)
    msg.body = f'Please click the following link to verify your email: {verification_url}'
    mail.send(msg)

@app.route('/')
def home():
    return jsonify({
        'message': 'Secure File Sharing API',
        'endpoints': {
            'client': {
                'signup': '/api/client/signup',
                'login': '/api/client/login',
                'list_files': '/api/client/files',
                'download': '/api/client/download/<file_id>'
            },
            'ops': {
                'login': '/api/ops/login',
                'upload': '/api/ops/upload',
                'list_files': '/api/ops/files',
                'delete_file': '/api/ops/files/delete/<file_id>'
            }
        }
    }), 200

@app.route('/api/ops/login', methods=['POST'])
def ops_login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email'], role='ops').first()
    
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/ops/upload', methods=['POST'])
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'ops':
        return jsonify({'message': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'message': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    unique_filename = f"{str(uuid.uuid4())}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    file.save(file_path)
    
    # Verify file type using mimetypes
    file_type = mimetypes.guess_type(filename)[0]
    if not file_type or not any(ext in file_type for ext in ['officedocument', 'spreadsheet', 'presentation']):
        os.remove(file_path)
        return jsonify({'message': 'Invalid file type'}), 400
    
    # Generate encrypted download token
    download_token = str(uuid.uuid4())
    
    new_file = File(
        filename=unique_filename,
        original_filename=filename,
        file_type=filename.rsplit('.', 1)[1].lower(),
        uploaded_by=user_id,
        download_token=download_token
    )
    
    db.session.add(new_file)
    db.session.commit()
    
    return jsonify({'message': 'File uploaded successfully'}), 201

@app.route('/api/client/signup', methods=['POST'])
def client_signup():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    verification_token = str(uuid.uuid4())
    
    new_user = User(
        email=data['email'],
        password=hashed_password,
        role='client',
        verification_token=verification_token
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Send verification email
    send_verification_email(data['email'], verification_token)
    
    return jsonify({'message': 'Please check your email for verification'}), 201

@app.route('/api/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return jsonify({'message': 'Invalid verification token'}), 400
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    
    return jsonify({'message': 'Email verified successfully'}), 200

@app.route('/api/client/login', methods=['POST'])
def client_login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email'], role='client').first()
    
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_verified:
        return jsonify({'message': 'Please verify your email first'}), 403
    
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

@app.route('/api/client/files', methods=['GET'])
@jwt_required()
def list_files():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'client':
        return jsonify({'message': 'Unauthorized'}), 403
    
    files = File.query.all()
    file_list = [{
        'id': file.id,
        'filename': file.original_filename,
        'type': file.file_type,
        'uploaded_at': file.created_at.isoformat()
    } for file in files]
    
    return jsonify({'files': file_list}), 200

@app.route('/api/client/download/<int:file_id>', methods=['GET'])
@jwt_required()
def get_download_link(file_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'client':
        return jsonify({'message': 'Unauthorized'}), 403
    
    file = File.query.get_or_404(file_id)
    
    # Generate encrypted download URL
    encrypted_token = fernet.encrypt(file.download_token.encode()).decode()
    download_url = url_for('download_file', token=encrypted_token, _external=True)
    
    return jsonify({
        'download_link': download_url,
        'message': 'success'
    }), 200

@app.route('/api/download/<token>')
@jwt_required()
def download_file(token):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'client':
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        decrypted_token = fernet.decrypt(token.encode()).decode()
        file = File.query.filter_by(download_token=decrypted_token).first()
        
        if not file:
            return jsonify({'message': 'Invalid download link'}), 404
        
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            file.filename,
            as_attachment=True,
            download_name=file.original_filename
        )
    except:
        return jsonify({'message': 'Invalid download link'}), 400

@app.route('/api/ops/files/delete/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file_route(file_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'ops':
        return jsonify({'message': 'Unauthorized'}), 403
    
    file = File.query.get_or_404(file_id)
    
    # Delete the physical file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete database record
    db.session.delete(file)
    db.session.commit()
    
    return jsonify({'message': 'File deleted successfully'}), 200

@app.route('/api/ops/files', methods=['GET'])
@jwt_required()
def list_files_ops():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'ops':
        return jsonify({'message': 'Unauthorized'}), 403
    
    files = File.query.all()
    file_list = [{
        'id': file.id,
        'filename': file.original_filename,
        'type': file.file_type,
        'uploaded_at': file.created_at.isoformat(),
        'uploaded_by': file.uploaded_by
    } for file in files]
    
    return jsonify({'files': file_list}), 200

@app.route('/api/files/search', methods=['GET'])
@jwt_required()
def search_files():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    query = request.args.get('q', '').lower()
    file_type = request.args.get('type')
    
    # Base query
    files_query = File.query
    
    # Apply search filters
    if query:
        files_query = files_query.filter(File.original_filename.ilike(f'%{query}%'))
    
    if file_type:
        files_query = files_query.filter(File.file_type == file_type)
    
    files = files_query.all()
    
    file_list = [{
        'id': file.id,
        'filename': file.original_filename,
        'type': file.file_type,
        'uploaded_at': file.created_at.isoformat(),
        'uploaded_by': file.uploaded_by if user.role == 'ops' else None
    } for file in files]
    
    return jsonify({
        'files': file_list,
        'total': len(file_list)
    }), 200 