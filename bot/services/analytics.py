"""
Аналитика и статистика бота
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter


class AnalyticsService:
    """Сервис аналитики"""
    
    def __init__(self, db):
        """
        Инициализация сервиса
        
        Args:
            db: Database repository
        """
        self.db = db
    
    def get_global_stats(self) -> Dict:
        """
        Получить глобальную статистику бота
        
        Returns:
            Словарь со статистикой
        """
        with self.db.get_session() as session:
            from database.models import User, Message
            
            total_users = session.query(User).count()
            active_users = session.query(User).filter(User.is_active == True).count()
            total_messages = session.query(Message).count()
            
            # Статистика по языкам
            users = session.query(User).all()
            languages = Counter([u.language for u in users])
            
            # Статистика по моделям
            messages = session.query(Message).all()
            models = Counter([m.model_used for m in messages])
            
            # Кеш статистика
            cached_messages = session.query(Message).filter(Message.is_cached == True).count()
            cache_hit_rate = (cached_messages / total_messages * 100) if total_messages > 0 else 0
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_messages': total_messages,
                'languages': dict(languages),
                'models_used': dict(models),
                'cache_hit_rate': round(cache_hit_rate, 2),
                'cached_messages': cached_messages
            }
    
    def get_user_activity(self, days: int = 7) -> Dict:
        """
        Получить активность пользователей за период
        
        Args:
            days: Количество дней
            
        Returns:
            Статистика активности
        """
        with self.db.get_session() as session:
            from database.models import User, Message
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Новые пользователи
            new_users = session.query(User).filter(
                User.created_at >= start_date
            ).count()
            
            # Активные пользователи (отправившие сообщения)
            active_users = session.query(Message.user_telegram_id).filter(
                Message.created_at >= start_date
            ).distinct().count()
            
            # Сообщения за период
            messages = session.query(Message).filter(
                Message.created_at >= start_date
            ).count()
            
            return {
                'period_days': days,
                'new_users': new_users,
                'active_users': active_users,
                'messages': messages,
                'avg_messages_per_user': round(messages / active_users, 2) if active_users > 0 else 0
            }
    
    def get_top_users(self, limit: int = 10) -> List[Dict]:
        """
        Получить топ пользователей по активности
        
        Args:
            limit: Количество пользователей
            
        Returns:
            Список топ пользователей
        """
        with self.db.get_session() as session:
            from database.models import User
            from sqlalchemy import desc
            
            users = session.query(User).order_by(
                desc(User.message_count)
            ).limit(limit).all()
            
            return [
                {
                    'telegram_id': u.telegram_id,
                    'username': u.username or 'Unknown',
                    'message_count': u.message_count,
                    'language': u.language,
                    'created_at': u.created_at.strftime('%Y-%m-%d')
                }
                for u in users
            ]
    
    def get_language_distribution(self) -> Dict[str, int]:
        """
        Получить распределение по языкам
        
        Returns:
            Словарь {язык: количество пользователей}
        """
        with self.db.get_session() as session:
            from database.models import User
            
            users = session.query(User).all()
            languages = Counter([u.language for u in users])
            
            return dict(languages)
    
    def get_model_usage_stats(self) -> Dict:
        """
        Получить статистику использования моделей AI
        
        Returns:
            Статистика по моделям
        """
        with self.db.get_session() as session:
            from database.models import Message
            
            messages = session.query(Message).all()
            models = Counter([m.model_used for m in messages])
            
            total = sum(models.values())
            
            return {
                'total_requests': total,
                'models': dict(models),
                'percentages': {
                    model: round(count / total * 100, 2)
                    for model, count in models.items()
                } if total > 0 else {}
            }
    
    def get_cache_efficiency(self) -> Dict:
        """
        Получить эффективность кеша
        
        Returns:
            Статистика кеша
        """
        with self.db.get_session() as session:
            from database.models import Message, Cache
            
            total_messages = session.query(Message).count()
            cached_messages = session.query(Message).filter(
                Message.is_cached == True
            ).count()
            
            cache_entries = session.query(Cache).count()
            total_hits = session.query(Cache).with_entities(
                Cache.hit_count
            ).all()
            total_hit_count = sum([h[0] for h in total_hits])
            
            hit_rate = (cached_messages / total_messages * 100) if total_messages > 0 else 0
            
            return {
                'total_messages': total_messages,
                'cached_responses': cached_messages,
                'cache_hit_rate': round(hit_rate, 2),
                'cache_entries': cache_entries,
                'total_cache_hits': total_hit_count,
                'avg_hits_per_entry': round(total_hit_count / cache_entries, 2) if cache_entries > 0 else 0
            }
    
    def export_user_data(self, telegram_id: int) -> Dict:
        """
        Экспорт всех данных пользователя
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Все данные пользователя
        """
        with self.db.get_session() as session:
            from database.models import User, Message
            
            user = session.query(User).filter(
                User.telegram_id == telegram_id
            ).first()
            
            if not user:
                return {}
            
            messages = session.query(Message).filter(
                Message.user_telegram_id == telegram_id
            ).all()
            
            return {
                'user': {
                    'telegram_id': user.telegram_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'language': user.language,
                    'message_count': user.message_count,
                    'created_at': user.created_at.isoformat(),
                    'is_active': user.is_active
                },
                'messages': [
                    {
                        'user_message': m.user_message,
                        'bot_response': m.bot_response,
                        'language': m.language,
                        'model_used': m.model_used,
                        'created_at': m.created_at.isoformat(),
                        'is_cached': m.is_cached
                    }
                    for m in messages
                ],
                'total_messages': len(messages)
            }
