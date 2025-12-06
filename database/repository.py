"""
Database repository для работы с БД
"""
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from .models import Base, User, Message, Cache


class DatabaseRepository:
    """Репозиторий для работы с базой данных"""
    
    def __init__(self, database_url: str):
        """
        Инициализация репозитория
        
        Args:
            database_url: URL подключения к PostgreSQL
        """
        # Используем NullPool для serverless окружения (Railway)
        self.engine = create_engine(
            database_url,
            poolclass=NullPool,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Создание таблиц
        Base.metadata.create_all(self.engine)
        print("✅ База данных инициализирована")
    
    def get_session(self) -> Session:
        """Получить сессию БД"""
        return self.SessionLocal()
    
    # === USER METHODS ===
    
    def get_or_create_user(
        self,
        telegram_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None
    ) -> User:
        """
        Получить или создать пользователя
        
        Args:
            telegram_id: Telegram ID пользователя
            username: Username
            first_name: Имя
            last_name: Фамилия
            
        Returns:
            User объект
        """
        with self.get_session() as session:
            user = session.query(User).filter(
                User.telegram_id == telegram_id
            ).first()
            
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"✅ Создан новый пользователь: {telegram_id}")
            
            return user
    
    def update_user_language(self, telegram_id: int, language: str):
        """Обновить язык пользователя"""
        with self.get_session() as session:
            user = session.query(User).filter(
                User.telegram_id == telegram_id
            ).first()
            
            if user:
                user.language = language
                session.commit()
    
    def increment_message_count(self, telegram_id: int):
        """Увеличить счетчик сообщений"""
        with self.get_session() as session:
            user = session.query(User).filter(
                User.telegram_id == telegram_id
            ).first()
            
            if user:
                user.message_count += 1
                session.commit()
    
    def get_user_stats(self, telegram_id: int) -> Dict:
        """Получить статистику пользователя"""
        with self.get_session() as session:
            user = session.query(User).filter(
                User.telegram_id == telegram_id
            ).first()
            
            if not user:
                return {}
            
            message_count = session.query(Message).filter(
                Message.user_telegram_id == telegram_id
            ).count()
            
            return {
                'message_count': user.message_count,
                'total_messages': message_count,
                'language': user.language,
                'created_at': user.created_at
            }
    
    # === MESSAGE METHODS ===
    
    def save_message(
        self,
        telegram_id: int,
        user_message: str,
        bot_response: str,
        language: str,
        model_used: str,
        is_cached: bool = False
    ):
        """
        Сохранить сообщение
        
        Args:
            telegram_id: Telegram ID пользователя
            user_message: Сообщение пользователя
            bot_response: Ответ бота
            language: Язык
            model_used: Использованная модель
            is_cached: Был ли ответ из кеша
        """
        with self.get_session() as session:
            message = Message(
                user_telegram_id=telegram_id,
                user_message=user_message,
                bot_response=bot_response,
                language=language,
                model_used=model_used,
                is_cached=is_cached
            )
            session.add(message)
            session.commit()
    
    def get_user_history(
        self,
        telegram_id: int,
        limit: int = 5
    ) -> List[Dict]:
        """
        Получить историю сообщений пользователя
        
        Args:
            telegram_id: Telegram ID пользователя
            limit: Количество последних сообщений
            
        Returns:
            Список сообщений
        """
        with self.get_session() as session:
            messages = session.query(Message).filter(
                Message.user_telegram_id == telegram_id
            ).order_by(
                Message.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    'user': msg.user_message,
                    'bot': msg.bot_response,
                    'timestamp': msg.created_at
                }
                for msg in reversed(messages)
            ]
    
    def clear_user_history(self, telegram_id: int):
        """Очистить историю пользователя"""
        with self.get_session() as session:
            session.query(Message).filter(
                Message.user_telegram_id == telegram_id
            ).delete()
            session.commit()
    
    # === CACHE METHODS ===
    
    @staticmethod
    def _hash_query(query: str) -> str:
        """Создать хеш запроса"""
        return hashlib.sha256(query.encode()).hexdigest()
    
    def get_cached_response(self, query: str) -> Optional[str]:
        """
        Получить ответ из кеша
        
        Args:
            query: Запрос
            
        Returns:
            Кешированный ответ или None
        """
        query_hash = self._hash_query(query)
        
        with self.get_session() as session:
            cache_entry = session.query(Cache).filter(
                and_(
                    Cache.query_hash == query_hash,
                    Cache.expires_at > datetime.now()
                )
            ).first()
            
            if cache_entry:
                # Увеличиваем счетчик попаданий
                cache_entry.hit_count += 1
                session.commit()
                return cache_entry.response
            
            return None
    
    def set_cached_response(
        self,
        query: str,
        response: str,
        ttl: int = 3600
    ):
        """
        Сохранить ответ в кеш
        
        Args:
            query: Запрос
            response: Ответ
            ttl: Время жизни в секундах
        """
        query_hash = self._hash_query(query)
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        with self.get_session() as session:
            # Проверяем существует ли уже
            existing = session.query(Cache).filter(
                Cache.query_hash == query_hash
            ).first()
            
            if existing:
                # Обновляем существующий
                existing.response = response
                existing.expires_at = expires_at
                existing.hit_count += 1
            else:
                # Создаем новый
                cache_entry = Cache(
                    query_hash=query_hash,
                    query_text=query,
                    response=response,
                    expires_at=expires_at
                )
                session.add(cache_entry)
            
            session.commit()
    
    def clear_expired_cache(self) -> int:
        """
        Очистить просроченный кеш
        
        Returns:
            Количество удаленных записей
        """
        with self.get_session() as session:
            deleted = session.query(Cache).filter(
                Cache.expires_at <= datetime.now()
            ).delete()
            session.commit()
            return deleted
