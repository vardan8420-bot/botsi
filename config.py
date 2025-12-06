import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Telegram
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL_CHEAP: str = 'gpt-4o-mini'
    OPENAI_MODEL_SMART: str = 'gpt-4o'
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7
    
    # Voice (Часть 2)
    ELEVENLABS_API_KEY: str = os.getenv('ELEVENLABS_API_KEY', '')
    WHISPER_MODEL: str = 'whisper-1'
    
    # Social Media (Часть 2)
    INSTAGRAM_USERNAME: str = os.getenv('INSTAGRAM_USERNAME', '')
    INSTAGRAM_PASSWORD: str = os.getenv('INSTAGRAM_PASSWORD', '')
    YOUTUBE_API_KEY: str = os.getenv('YOUTUBE_API_KEY', '')
    
    # GitHub (Часть 4)
    GITHUB_TOKEN: str = os.getenv('GITHUB_TOKEN', '')
    
    # Qdrant
    QDRANT_URL: str = os.getenv('QDRANT_URL', 'http://localhost:6333')
    QDRANT_API_KEY: str = os.getenv('QDRANT_API_KEY', '')
    
    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    
    # Budget
    MAX_DAILY_SPEND: float = 3.33
    
    # Railway
    PORT: int = int(os.getenv('PORT', 8080))

