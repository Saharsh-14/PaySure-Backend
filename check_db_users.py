import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User

def check_users():
    try:
        db = SessionLocal()
        users = db.query(User).all()
        print(f"Total users in 'clerks' table: {len(users)}")
        for u in users:
            print(f"ID: {u.clerk_id} | Email: {u.email} | Role: {u.role}")
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
