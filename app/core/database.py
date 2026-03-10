from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Use the formatted URL which handles Neon SSL requirements
DATABASE_URL = settings.get_database_url

# Step 2: SQLAlchemy Engine Setup for Serverless
# Configure connection pooling limits, pool_pre_ping to check for severed connections
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Crucial for Neon to handle serverless connection drops
    pool_size=5,         # Keep base connection pool small
    max_overflow=10      # Allow up to 10 extra temporary connections during bursts
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

# Step 6: Database Session Dependency (already correctly implemented)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
