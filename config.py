"""
Botsi - AI Super Bot
Конфигурация приложения
"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


class Config:
    """Конфигурация бота"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL_MINI = 'gpt-4o-mini'
    OPENAI_MODEL_FULL = 'gpt-4o'
    GPT4O_PROBABILITY = float(os.getenv('GPT4O_PROBABILITY', '0.05'))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Cache
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))
    
    # Context
    MAX_CONTEXT_MESSAGES = int(os.getenv('MAX_CONTEXT_MESSAGES', '5'))
    
    # Optional APIs (с fallback)
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
    INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    TIKTOK_SESSION_ID = os.getenv('TIKTOK_SESSION_ID')
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    
    @classmethod
    def validate(cls):
        """Валидация обязательных параметров"""
        required = {
            'TELEGRAM_BOT_TOKEN': cls.TELEGRAM_BOT_TOKEN,
            'OPENAI_API_KEY': cls.OPENAI_API_KEY,
            'DATABASE_URL': cls.DATABASE_URL,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(
                f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing)}"
            )
        
        return True
