from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os

DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    subscription_end = Column(DateTime, default=datetime.utcnow() - timedelta(days=1))
    request_count = Column(Integer, default=0)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_user(telegram_id: str):
    session = SessionLocal()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()
    return user

def update_subscription(telegram_id: str, days: int = 30):
    session = SessionLocal()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.subscription_end = datetime.utcnow() + timedelta(days=days)
        session.commit()

def can_use_bot(telegram_id: str) -> bool:
    user = get_user(telegram_id)
    return user.subscription_end > datetime.utcnow()
