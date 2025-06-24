# Secure File-Sharing System

A secure file-sharing system built with Flask that allows Operations Users to upload files and Client Users to download them through encrypted URLs.

## Features

- Two types of users: Operations (Ops) and Client
- Secure file upload (only .pptx, .docx, and .xlsx files)
- Email verification for client users
- Encrypted download URLs
- JWT-based authentication
- File type verification using magic numbers

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A Gmail account for sending verification emails

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```
SECRET_KEY=your-secret-key-here
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
UPLOAD_FOLDER=uploads
DATABASE_URL=sqlite:///database.db
```

Note: For the Gmail password, you'll need to generate an App Password. Go to your Google Account settings > Security > 2-Step Verification > App passwords

5. Create the database:
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Operations User

1. Login:
```
POST /api/ops/login
Content-Type: application/json

{
    "email": "ops@example.com",
    "password": "password123"
}
```

2. Upload File:
```
POST /api/ops/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file>
```

### Client User

1. Sign Up:
```
POST /api/client/signup
Content-Type: application/json

{
    "email": "client@example.com",
    "password": "password123"
}
```

2. Login:
```
POST /api/client/login
Content-Type: application/json

{
    "email": "client@example.com",
    "password": "password123"
}
```

3. List Files:
```
GET /api/client/files
Authorization: Bearer <token>
```

4. Get Download Link:
```
GET /api/client/download/<file_id>
Authorization: Bearer <token>
```

## Running Tests

```bash
pytest tests/
```

## Deployment

For production deployment:

1. Use a production-grade WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn app:app
```

2. Set up a reverse proxy (e.g., Nginx) to handle static files and SSL termination

3. Use environment variables for all sensitive configuration

4. Set up monitoring and logging

5. Use a production-grade database (e.g., PostgreSQL)

## Security Features

- Password hashing using bcrypt
- JWT-based authentication
- Email verification for new users
- File type verification using magic numbers
- Encrypted download URLs
- Role-based access control 