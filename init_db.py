from app.core.database import engine, Base
import app.models # This triggers all imports in app.models.__init__.py

def init_db():
    print("Initializing missing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Successfully synchronized all tables.")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
