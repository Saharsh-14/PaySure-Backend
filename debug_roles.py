from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    emails = ["saurabhcomputers77@gmail.com", "saharshjais1423@gmail.com"]
    for email in emails:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"USER {email}: Database Role = {user.role.value if hasattr(user.role, 'value') else user.role}")
        else:
            print(f"USER {email}: Not found in database")
finally:
    db.close()
