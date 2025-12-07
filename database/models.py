"""
Database models для Botsi
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    language = Column(String(10), default='hy')  # hy, ru, en
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)


class Message(Base):
    """Модель сообщения"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(Integer, nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    language = Column(String(10))
    model_used = Column(String(50))  # gpt-4o-mini или gpt-4o
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_cached = Column(Boolean, default=False)


class Cache(Base):
    """Модель кеша"""
    __tablename__ = 'cache'
    
    id = Column(Integer, primary_key=True)
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)


class ScheduledPost(Base):
    """Задача на отложенную публикацию в соцсети"""
    __tablename__ = 'scheduled_posts'

    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)  # 'Instagram' | 'Facebook'
    caption = Column(Text, nullable=False)
    telegram_file_id = Column(String(255))  # Для Instagram фото
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default='pending')  # pending | posted | failed | canceled
    attempt_count = Column(Integer, default=0)
    last_error = Column(Text)
    created_by = Column(Integer)  # Telegram ID автора задачи
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
