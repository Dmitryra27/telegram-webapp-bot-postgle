from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()
# Получаем URL из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден. Пожалуйста, установите переменную окружения.")

# Используем новый ORM Base из SQLAlchemy 2.0
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    subscription_type = Column(String(50), default='free')
    subscription_end = Column(DateTime, default=datetime.now(timezone.utc) - timedelta(days=1))
    request_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


# --- Защита от падения при старте ---
# Создаём движок
engine = None
SessionLocal = None

try:
    engine = create_engine(DATABASE_URL)
    # Проверяем подключение
    engine.connect().close()
    print("✅ Подключение к БД прошло успешно")

    SessionLocal = sessionmaker(bind=engine)

except Exception as e:
    print(f"❌ Ошибка подключения к БД: {e}")


def get_session():
    if SessionLocal is None:
        raise Exception("Не удалось подключиться к базе данных")
    return SessionLocal()


def get_user(telegram_id: str):
    if SessionLocal is None:
        raise Exception("База данных недоступна")

    session = get_session()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()
    return user


def update_subscription(telegram_id: str, days: int = 30):
    if SessionLocal is None:
        raise Exception("База данных недоступна")

    session = get_session()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.subscription_end = datetime.now(timezone.utc) + timedelta(days=days)
        session.commit()


def can_use_bot(telegram_id: str) -> bool:
    try:
        user = get_user(telegram_id)
        return user.subscription_end > datetime.now(timezone.utc)
    except:
        print("⚠️ База данных не доступна — работа в режиме ограниченной функциональности")
        return False  # или True, в зависимости от политики
