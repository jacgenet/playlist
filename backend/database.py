from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - defaults to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spin_playlist.db")

print(f"Database URL: {DATABASE_URL}")  # Debug logging

try:
    # For production PostgreSQL
    if DATABASE_URL.startswith("postgresql"):
        engine = create_engine(DATABASE_URL)
    else:
        # SQLite for development
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("Database connection established successfully")
    
except Exception as e:
    print(f"Database connection error: {e}")
    # Fallback to in-memory SQLite
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("Using fallback in-memory database")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
