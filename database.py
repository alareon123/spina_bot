from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_pain_rating = Column(Integer, nullable=True)
    last_rating_date = Column(DateTime, nullable=True)

class VideoLesson(Base):
    __tablename__ = 'video_lessons'
    
    id = Column(Integer, primary_key=True)
    pain_level = Column(Integer, nullable=False)  # 1-5
    file_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # в секундах
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_admin = Column(Integer, nullable=False)

class BotSettings(Base):
    __tablename__ = 'bot_settings'
    
    id = Column(Integer, primary_key=True)
    setting_name = Column(String, unique=True, nullable=False)
    setting_value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by_admin = Column(Integer, nullable=False)

class UserResponse(Base):
    __tablename__ = 'user_responses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    pain_rating = Column(Integer, nullable=False)
    response_date = Column(DateTime, default=datetime.utcnow)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///spina_bot.db')

# Создаем директорию для базы данных если её нет
if DATABASE_URL.startswith('sqlite:///'):
    db_path = DATABASE_URL.replace('sqlite:///', '')
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_default_settings():
    """Инициализация настроек по умолчанию"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже настройки
        if not db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_hour').first():
            default_settings = [
                BotSettings(setting_name='reminder_hour', setting_value='10', updated_by_admin=354786612),
                BotSettings(setting_name='reminder_minute', setting_value='0', updated_by_admin=354786612),
                BotSettings(setting_name='reminder_enabled', setting_value='true', updated_by_admin=354786612)
            ]
            for setting in default_settings:
                db.add(setting)
            db.commit()
    finally:
        db.close() 