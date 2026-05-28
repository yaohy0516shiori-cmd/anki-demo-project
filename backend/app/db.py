from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.settings import settings

# create a sqlalchemy engine, connect to the database
engine = create_engine(settings.database_url,pool_pre_ping=True)

# create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# get a database session, each request will create a new session, FastAPI dependency injection uses database session
def get_db() -> Generator[Session, None, None]:
    # create a session
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()