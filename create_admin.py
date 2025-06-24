from app import app, db, bcrypt
from models import User

def create_ops_user(email, password):
    with app.app_context():
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            print("User already exists!")
            return
        
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new ops user
        new_user = User(
            email=email,
            password=hashed_password,
            role='ops',
            is_verified=True  # Ops users don't need email verification
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        print(f"Ops user {email} created successfully!")

if __name__ == "__main__":
    # Admin credentials
    admin_email = "shivvshiv109@gmail.com"
    admin_password = "admin123"
    
    create_ops_user(admin_email, admin_password) 