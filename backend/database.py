from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config
import os

DATABASE_URL = f"sqlite:///{os.path.join(Config.DATA_DIR, 'documents.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from models import Document
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)
