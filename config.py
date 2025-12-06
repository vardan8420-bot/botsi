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
    
    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    
    # Budget
    MAX_DAILY_SPEND: float = 3.33
    
    # Railway
    PORT: int = int(os.getenv('PORT', 8080))
