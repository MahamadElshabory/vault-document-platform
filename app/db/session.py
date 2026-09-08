from sqlmodel import Session, create_engine

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)


def get_db():
    with Session(engine) as session:
        yield session




"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings



engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        
        """