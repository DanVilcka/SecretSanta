from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from models import create_engine
from config import DATABASE_URL
from models import Participant, Wish
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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

def save_name(session, user_id, name_text, username):
    logger.info(f"Save name for user {user_id} '{name_text}' to db")
    participant = session.query(Participant).filter_by(user_id=user_id).first()
    if not participant:
        new_particiant = Participant(user_id=user_id, name=name_text, username=username)
        session.add(new_particiant)
        session.commit()

def save_wish(session, user_id, wish_text):
    logger.info(f"Save wish for user {user_id} '{wish_text}' to db")
    
    participant = session.query(Participant).filter_by(user_id=user_id).first()
    if not participant:
        raise ValueError("Пользователь не найден в базе данных")
    
    # Создаем новый объект Wish и добавляем его в сессию
    new_wish = Wish(user_id=user_id, wish_text=wish_text)
    session.add(new_wish)
    session.commit()  # Фиксируем изменения

def update_wish(session, user_id, new_wish_text):
    # Проверяем, существует ли пользователь в базе данных
    logger.info(f"Start updating wish for user {user_id} from '{new_wish_text}' to db")
    participant = session.query(Participant).filter_by(user_id=user_id).first()
    if not participant:
        raise ValueError("Пользователь не найден в базе данных")
    
    # Обновляем желание пользователя
    wish = session.query(Wish).filter_by(user_id=user_id).first()
    if wish:
        logger.info(f"Updating wish for user {user_id} from '{wish.wish_text}' to '{new_wish_text}'")
        wish.wish_text = new_wish_text
        session.commit()  # Фиксируем изменения
    else:
        logger.info(f"Creating new wish for user {user_id}: '{new_wish_text}'")
        new_wish = Wish(user_id=user_id, wish_text=new_wish_text)
        session.add(new_wish)
        session.commit()  # Фиксируем изменения

def list_participants(session):
    return session.query(Participant).all()

def list_wish_with_id(session, user_id):
    return session.query(Wish).filter_by(user_id=user_id).first()