import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file
load_dotenv()

# Read database URL from environment variable, default to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local_users.db")

# Setup connection arguments based on database type
connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    connect_args["connect_timeout"] = 3
elif DATABASE_URL.startswith("sqlite"):
    # SQLite connection requires check_same_thread=False for multi-threaded FastAPI apps
    connect_args["check_same_thread"] = False

# Initialize the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create a sessionmaker factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()

# FastAPI dependency to handle database session lifecycle
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()