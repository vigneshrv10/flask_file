from app import app, db, bcrypt
from models import User

def create_client_user(email, password):
    with app.app_context():
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            print("User already exists!")
            return
        
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new client user
        new_user = User(
            email=email,
            password=hashed_password,
            role='client',
            is_verified=True  # Setting to True for testing purposes
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        print(f"Client user {email} created successfully!")

if __name__ == "__main__":
    # Client credentials
    client_email = "client@example.com"
    client_password = "client123"
    
    create_client_user(client_email, client_password) 