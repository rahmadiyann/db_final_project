from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

engine = create_engine('postgresql://user:password@localhost:5432/postgres_db', pool_pre_ping=True, pool_recycle=300)

def get_session():
    from scripts.models import Base
    Base.metadata.create_all(bind=engine)
    # engine = create_engine(os.getenv('POSTGRES_URL_SOURCE'), pool_pre_ping=True, pool_recycle=300)
    # engine = create_engine('postgresql://default:AVb2Io9pqyWm@ep-super-shape-a12kklqk.ap-southeast-1.aws.neon.tech:5432/verceldb', pool_pre_ping=True, pool_recycle=300)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

session = get_session()