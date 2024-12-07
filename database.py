from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Get the DATABASE_URL from environment variable, with a default SQLite URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./construction_crm.db")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Render provides PostgreSQL URLs starting with postgres://, but SQLAlchemy needs postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

logger.info(f"Using database URL type: {'PostgreSQL' if DATABASE_URL and 'postgresql' in DATABASE_URL else 'SQLite'}")

if not DATABASE_URL:
    # Default to SQLite for local development
    DATABASE_URL = "sqlite:///./construction_crm.db"
    logger.info("No DATABASE_URL found, using SQLite database")

# Create SQLAlchemy engine with proper arguments based on database type
if DATABASE_URL.startswith("postgresql://"):
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_pre_ping=True,
        pool_recycle=300
    )
    logger.info("Created PostgreSQL engine with connection pooling")
else:
    # SQLite engine doesn't support the same connection pool parameters
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    logger.info("Created SQLite engine")

try:
    # Test the database connection
    with engine.connect() as conn:
        logger.info("Successfully connected to database")
except Exception as e:
    logger.error(f"Failed to connect to database: {str(e)}")
    raise

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
