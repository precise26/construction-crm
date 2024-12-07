import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import urllib.parse
import traceback

logger = logging.getLogger(__name__)

# Get the DATABASE_URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Log the raw DATABASE_URL for debugging
logger.info(f"Raw DATABASE_URL: {DATABASE_URL}")

# Validate and transform the DATABASE_URL
if DATABASE_URL:
    # Ensure the URL is properly parsed
    try:
        parsed_url = urllib.parse.urlparse(DATABASE_URL)
        logger.info(f"Parsed URL - Scheme: {parsed_url.scheme}, Hostname: {parsed_url.hostname}")
    except Exception as e:
        logger.error(f"Error parsing DATABASE_URL: {e}")

    # Handle Render's PostgreSQL URL format
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        logger.info("Converted postgres:// to postgresql://")
else:
    # Fallback to SQLite for local development
    DATABASE_URL = "sqlite:///./construction_crm.db"
    logger.warning("No DATABASE_URL found, using SQLite as fallback")

# Mask sensitive parts of the connection string for logging
masked_url = DATABASE_URL
if '@' in masked_url:
    parts = masked_url.split('@')
    masked_url = f"{parts[0][:10]}...@{parts[1]}"
logger.info(f"Processed DATABASE_URL: {masked_url}")

# Create SQLAlchemy engine with robust connection settings
try:
    if DATABASE_URL.startswith("postgresql://"):
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5
            }
        )
        logger.info("Created PostgreSQL engine with advanced connection pooling")
    else:
        # SQLite configuration
        engine = create_engine(
            DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
        logger.info("Created SQLite engine")

    # Test the database connection
    with engine.connect() as conn:
        logger.info("Successfully established database connection")

except Exception as e:
    logger.error(f"Database connection error: {str(e)}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
