"""
Умный обработчик AI запросов
- 95% запросов → GPT-4o-mini ($0.15/1M input)
- 5% сложных → GPT-4o ($2.50/1M input)
- Автоматическое определение сложности
- Бюджет: $3.33/день ($100/месяц)
"""
from typing import Optional, List, Dict
from openai import OpenAI
from config import Config


class AIHandler:
    """
    Умный обработчик AI запросов с экономией бюджета
    """
    
    def __init__(self, config: Config):
        """
        Инициализация AI обработчика
        
        Args:
            config: Конфигурация бота
        """
        self.config = config
        self.client = None
        
        if config.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
                print("✅ OpenAI клиент инициализирован успешно")
            except Exception as e:
                print(f"❌ Ошибка при инициализации OpenAI: {e}")
        else:
            print("⚠️ OpenAI API ключ не найден")
    
    def should_use_smart_model(self, message: str) -> bool:
        """
        Определяет нужна ли умная модель (GPT-4o)
        
        Args:
            message: Сообщение пользователя
            
        Returns:
            True если нужна умная модель
        """
        complex_keywords = [
            # Русские
            'анализ', 'прогноз', 'стратегия', 'код', 'программ',
            'сложн', 'детальн', 'разработк', 'проект', 'архитектур',
            'алгоритм', 'оптимизац', 'рефакторинг',
            
            # Армянские (транслит)
            'վերլուծություն', 'կանխատեսում', 'ծրագիր', 'ծրագրավորում',
            'vеrlyutsutyun', 'kanxatesum', 'tsragir', 'tsragravorum',
            
            # Английские
            'analyze', 'forecast', 'strategy', 'code', 'program',
            'complex', 'detailed', 'development', 'project', 'architecture',
            'algorithm', 'optimization', 'refactoring'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in complex_keywords)
    
    async def get_response(
        self,
        user_message: str,
        user_context: Dict,
        language: str = 'hy',
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Получает ответ от AI с учётом контекста
        
        Args:
            user_message: Сообщение пользователя
            user_context: Контекст пользователя (история разговора)
            language: Язык ответа ('hy', 'ru', 'en')
            system_prompt: Системный промпт (если None, используется по умолчанию)
            
        Returns:
            Ответ от AI или None при ошибке
        """
        if not self.client:
            return None
        
        try:
            # Выбор модели
            model = (
                self.config.OPENAI_MODEL_SMART
                if self.should_use_smart_model(user_message)
                else self.config.OPENAI_MODEL_CHEAP
            )
            
            # Формирование сообщений
            messages = []
            
            # Системный промпт
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            # История разговора (последние 5 сообщений)
            history = user_context.get('history', [])
            for msg in history[-5:]:
                if 'user' in msg:
                    messages.append({
                        'role': 'user',
                        'content': msg['user']
                    })
                if 'bot' in msg:
                    messages.append({
                        'role': 'assistant',
                        'content': msg['bot']
                    })
            
            # Текущее сообщение
            messages.append({
                'role': 'user',
                'content': user_message
            })
            
            # Запрос к OpenAI
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=self.config.OPENAI_MAX_TOKENS,
                temperature=self.config.OPENAI_TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Ошибка при запросе к OpenAI: {e}")
            return None
    
    def get_model_stats(self) -> Dict:
        """
        Получить статистику использования моделей
        
        Returns:
            Словарь со статистикой
        """
        # TODO: Реализовать отслеживание использования моделей
        return {
            'cheap_model': self.config.OPENAI_MODEL_CHEAP,
            'smart_model': self.config.OPENAI_MODEL_SMART,
            'max_daily_spend': self.config.MAX_DAILY_SPEND
        }

