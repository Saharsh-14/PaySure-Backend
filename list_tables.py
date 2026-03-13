from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    print("Tables in public schema:")
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    for row in result:
        print(row[0])
