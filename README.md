# Secure File Sharing System

A secure file-sharing system built with Flask that enables Operations users to upload files and Client users to download them securely through encrypted URLs.

## Tech Stack

- **Backend Framework**: Flask 3.0.2
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Email Service**: Flask-Mail with Gmail SMTP
- **File Encryption**: Fernet (cryptography)
- **Password Hashing**: Bcrypt
- **Deployment**: Render.com

## Features

### Operations User
- Secure login with JWT authentication
- File upload functionality (restricted to .pptx, .docx, and .xlsx)
- File management capabilities
- Role-based access control

### Client User
- Secure signup with email verification
- JWT-based authentication
- View available files
- Download files through encrypted URLs
- Access control based on user roles

## Security Features
- Password hashing using bcrypt
- JWT-based authentication for API endpoints
- Email verification for new users
- Encrypted download URLs using Fernet
- File type validation
- Role-based access control
- Secure file storage

## API Endpoints

### Operations User Endpoints
```
POST /api/ops/login
- Login for operations users
- Required fields: email, password

POST /api/ops/upload
- Upload files (only .pptx, .docx, .xlsx)
- Requires JWT authentication
- Form data: file

GET /api/ops/files
- List all uploaded files
- Requires JWT authentication

DELETE /api/ops/files/delete/<file_id>
- Delete a specific file
- Requires JWT authentication
```

### Client User Endpoints
```
POST /api/client/signup
- Register new client user
- Required fields: email, password

POST /api/client/login
- Login for client users
- Required fields: email, password

GET /api/client/files
- List available files
- Requires JWT authentication

GET /api/client/download/<file_id>
- Get encrypted download URL
- Requires JWT authentication

GET /api/download/<token>
- Download file using encrypted URL
- Requires valid token
```

## Setup Instructions

1. **Clone the Repository**
```bash
git clone <repository-url>
cd <repository-name>
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Variables**
Create a `.env` file with the following variables:
```
SECRET_KEY=your_secret_key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
DATABASE_URL=your_postgresql_url
UPLOAD_FOLDER=uploads
```

4. **Initialize Database**
```python
from app import db
db.create_all()
```

5. **Run the Application**
```bash
gunicorn app:app
```

## Usage Examples

### Operations User

1. **Login**
```bash
curl -X POST http://localhost:5000/api/ops/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ops@example.com", "password": "password"}'
```

2. **Upload File**
```bash
curl -X POST http://localhost:5000/api/ops/upload \
  -H "Authorization: Bearer <your_jwt_token>" \
  -F "file=@/path/to/document.xlsx"
```

### Client User

1. **Signup**
```bash
curl -X POST http://localhost:5000/api/client/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "client@example.com", "password": "password"}'
```

2. **Download File**
```bash
# First get the download URL
curl -X GET http://localhost:5000/api/client/download/<file_id> \
  -H "Authorization: Bearer <your_jwt_token>"

# Then use the returned URL to download the file
curl -X GET http://localhost:5000/api/download/<encrypted_token>
```

## Deployment

The application is deployed on Render.com with the following configuration:

1. **Web Service Settings**
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Python Version: 3.9.18

2. **Environment Variables**
All environment variables mentioned in the setup section should be configured in the Render dashboard.

3. **Database**
PostgreSQL database is provisioned through Render.com's database service.

## Security Considerations

1. **File Upload Security**
- Only allowed file types (.pptx, .docx, .xlsx)
- Secure filename generation
- File type verification

2. **User Authentication**
- JWT-based authentication
- Password hashing
- Email verification

3. **Download Security**
- Encrypted download URLs
- Time-limited access
- Role-based access control

## Error Handling

The API includes comprehensive error handling for:
- Invalid file types
- Unauthorized access
- Invalid tokens
- File not found
- Server errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 