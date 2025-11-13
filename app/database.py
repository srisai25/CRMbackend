import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .config import config
from .exceptions import DatabaseError

logger = logging.getLogger(__name__)

# SQLAlchemy setup
engine = None
SessionLocal = None
Base = declarative_base()

def init_database():
    """Initialize database connection."""
    global engine, SessionLocal
    
    try:
        # Create engine
        engine = create_engine(
            config.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        logger.info("MySQL database connection initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize MySQL database: {str(e)}")
        raise DatabaseError(f"Database initialization failed: {str(e)}")

def get_db() -> Session:
    """
    Get database session for dependency injection.
    
    Returns:
        SQLAlchemy Session instance
        
    Raises:
        DatabaseError: If database not initialized
    """
    if not SessionLocal:
        raise DatabaseError("Database not initialized. Please check MySQL configuration.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables."""
    try:
        if not engine:
            raise DatabaseError("Database engine not initialized")
            
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise DatabaseError(f"Table creation failed: {str(e)}")

# Initialize database on import
init_database()
