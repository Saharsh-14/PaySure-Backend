from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.models.user import User, UserRole
from app.core.database import SessionLocal

load_dotenv()

db = SessionLocal()
try:
    print("Seeding user via SQLAlchemy...")
    user_email = 'saurabhcomputers77@gmail.com'
    existing = db.query(User).filter(User.email == user_email).first()
    if not existing:
        new_user = User(
            clerk_id='user_2oX_placeholder_123',
            email=user_email,
            full_name='Saurabh Singh',
            role=UserRole.FREELANCER
        )
        db.add(new_user)
        db.commit()
        print(f"User {user_email} seeded successfully.")
    else:
        print(f"User {user_email} already exists.")
except Exception as e:
    print(f"ERROR: {e}")
    db.rollback()
finally:
    db.close()
