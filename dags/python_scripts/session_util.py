from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

def get_session():
    engine = create_engine(os.getenv('DATAENG_POSTGRES_URI'), pool_pre_ping=True, pool_recycle=300)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

session = get_session()