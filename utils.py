from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from models import create_engine
from config import DATABASE_URL

def create_session():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

@contextmanager
def session_scope():
    session = create_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()