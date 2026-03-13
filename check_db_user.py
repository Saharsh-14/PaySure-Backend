from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found")
    exit(1)

# Mask password for printing
from urllib.parse import urlparse
parsed = urlparse(DATABASE_URL)
masked_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}{parsed.path}"
print(f"Connecting to: {masked_url}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT clerk_id, email, full_name, role FROM clerks WHERE email ILIKE 'saurabhcomputers77@gmail.com'"))
        user = result.fetchone()
        if user:
            print(f"FOUND: {user}")
        else:
            print("NOT FOUND IN DB")
            
        # Check all users
        print("\nAll users in clerks table (limit 10):")
        result = conn.execute(text("SELECT email, role FROM clerks LIMIT 10"))
        for row in result:
            print(row)
except Exception as e:
    print(f"ERROR: {str(e)}")
