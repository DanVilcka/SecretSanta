from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config import DATABASE_URL

Base = declarative_base()

class Participant(Base):
    __tablename__ = 'participants'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    name = Column(String)
    username = Column(String)
    recipient_id = Column(Integer, ForeignKey('participants.user_id'))
    recipient = relationship("Participant", remote_side=[user_id])

def create_tables():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)