from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """
    Create database connection URL for Cloud SQL or local PostgreSQL
    """
    env = os.getenv("ENV", "development")
    
    if env == "production":
        # Cloud SQL connection using Cloud SQL Proxy
        try:
            from google.cloud.sql.connector import Connector
            
            instance_connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
            db_user = os.getenv("DB_USER", "postgres")
            db_pass = os.getenv("DB_PASSWORD")
            db_name = os.getenv("DB_NAME", "codeaudit")
            
            connector = Connector()
            
            def getconn():
                return connector.connect(
                    instance_connection_name,
                    "pg8000",
                    user=db_user,
                    password=db_pass,
                    db=db_name
                )
            
            engine = create_engine(
                "postgresql+pg8000://",
                creator=getconn,
                pool_size=5,
                max_overflow=2,
                pool_timeout=30,
                pool_recycle=1800,
            )
            return engine
        except ImportError:
            print("Warning: google-cloud-sql-connector not installed. Falling back to DATABASE_URL")
    
    # Local development or fallback
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/codeaudit")
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    return engine

# Create engine
engine = get_database_url()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency for FastAPI to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all tables in the database
    """
    from database.models import Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def drop_tables():
    """
    Drop all tables in the database (use with caution!)
    """
    from database.models import Base
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped!")
