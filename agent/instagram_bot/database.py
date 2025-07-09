import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from . import models
    logging.info("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    logging.info("Database tables created.")