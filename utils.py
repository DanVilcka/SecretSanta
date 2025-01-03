from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from models import create_engine
from config import DATABASE_URL
from models import Participant, Wish, GiftExchange, GiftExchangeCheck
import logging

logging.basicConfig(
    level=logging.WARNING, 
    filename = "logger.log", 
    format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s", 
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)

def create_session():
    try:
        engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
        Session = sessionmaker(bind=engine)
        session = Session()

        logging.info("Подключение к PostgreSQL установлено успешно")

    except Exception as error:
        logger.error("Ошибка при подключении к PostgreSQL: {error}")

    finally:
        if session:
            session.close()
            logging.info("Соединение с PostgreSQL закрыто")
    
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
    logger.warning(f"Save name for user {user_id} '{name_text}' to db")
    participant = session.query(Participant).filter_by(user_id=user_id).first()
    if not participant:
        new_particiant = Participant(user_id=user_id, name=name_text, username=username)
        session.add(new_particiant)
        session.commit()

def save_wish(session, user_id, wish_text):
    logger.warning(f"Save wish for user {user_id} '{wish_text}' to db")
    
    participant = session.query(Participant).filter_by(user_id=user_id).first()
    if not participant:
        raise ValueError("Пользователь не найден в базе данных")
    
    new_wish = Wish(user_id=user_id, wish_text=wish_text)
    session.add(new_wish)
    session.commit()

def update_wish(session, user_id, new_wish_text):
    logger.warning(f"Start updating wish for user {user_id} from '{new_wish_text}' to db")
    participant = session.query(Participant).filter_by(user_id=user_id).first()
    if not participant:
        raise ValueError("Пользователь не найден в базе данных")

    wish = session.query(Wish).filter_by(user_id=user_id).first()
    if wish:
        logger.warning(f"Updating wish for user {user_id} from '{wish.wish_text}' to '{new_wish_text}'")
        wish.wish_text = new_wish_text
        session.commit()
    else:
        logger.warning(f"Creating new wish for user {user_id}: '{new_wish_text}'")
        new_wish = Wish(user_id=user_id, wish_text=new_wish_text)
        session.add(new_wish)
        session.commit()

def add_gift_exchange(session, participant_id, receiver_id):
    gift_exchange = GiftExchange(participant_id=participant_id, receiver_id=receiver_id)
    session.add(gift_exchange)
    session.commit()

def add_gift_exchange(session, participant_id, receiver_id):
    gift_exchange = GiftExchange(participant_id=participant_id, receiver_id=receiver_id)
    session.add(gift_exchange)
    session.commit()

def add_gift_exchange_check(session, participant_id, receiver_id):
    gift_exchange = GiftExchangeCheck(participant_id=participant_id, receiver_id=receiver_id)
    session.add(gift_exchange)
    session.commit()

def clear_gift_exchange(session):
    session.query(GiftExchangeCheck).delete()
    session.commit()

def list_all_participants(session):
    return session.query(Participant).all()

def list_participant_with_id(session, user_id):
    return session.query(Participant).filter_by(user_id=user_id).first()

def list_wish_with_id(session, user_id):
    return session.query(Wish).filter_by(user_id=user_id).first()

def is_distribution_active(session):
    return session.query(GiftExchange).count()