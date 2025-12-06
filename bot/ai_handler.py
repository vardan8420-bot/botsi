"""
AI обработчик для работы с OpenAI
"""
import random
from typing import List, Dict, Optional
from openai import OpenAI


class AIHandler:
    """Обработчик AI запросов"""
    
    def __init__(self, api_key: str, model_mini: str, model_full: str, gpt4o_probability: float):
        """
        Инициализация AI обработчика
        
        Args:
            api_key: OpenAI API ключ
            model_mini: Модель GPT-4o-mini
            model_full: Модель GPT-4o
            gpt4o_probability: Вероятность использования GPT-4o (0.0-1.0)
        """
        self.client = OpenAI(api_key=api_key)
        self.model_mini = model_mini
        self.model_full = model_full
        self.gpt4o_probability = gpt4o_probability
    
    def _select_model(self, user_message: str) -> str:
        """
        Выбрать модель на основе сложности запроса
        
        Args:
            user_message: Сообщение пользователя
            
        Returns:
            Название модели
        """
        # Ключевые слова для сложных запросов
        complex_keywords = [
            'анализ', 'сравни', 'объясни подробно', 'разработай',
            'создай план', 'стратегия', 'алгоритм', 'код',
            'վերլուծություն', 'համեմատել', 'բացատրել',
            'analysis', 'compare', 'explain', 'develop', 'strategy'
        ]
        
        # Проверка на сложность
        is_complex = any(keyword in user_message.lower() for keyword in complex_keywords)
        
        # Длинные сообщения считаем сложными
        is_long = len(user_message) > 200
        
        if is_complex or is_long:
            # Для сложных запросов используем GPT-4o чаще
            return self.model_full if random.random() < 0.2 else self.model_mini
        else:
            # Для простых запросов используем GPT-4o редко
            return self.model_full if random.random() < self.gpt4o_probability else self.model_mini
    
    async def get_response(
        self,
        user_message: str,
        system_prompt: str,
        history: List[Dict] = None,
        language: str = 'hy'
    ) -> tuple[str, str]:
        """
        Получить ответ от AI
        
        Args:
            user_message: Сообщение пользователя
            system_prompt: Системный промпт
            history: История сообщений
            language: Язык ответа
            
        Returns:
            Tuple (ответ, использованная модель)
        """
        try:
            # Выбор модели
            model = self._select_model(user_message)
            
            # Формирование сообщений
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Добавление истории
            if history:
                for msg in history[-5:]:  # Последние 5 сообщений
                    messages.append({"role": "user", "content": msg['user']})
                    messages.append({"role": "assistant", "content": msg['bot']})
            
            # Текущее сообщение
            messages.append({"role": "user", "content": user_message})
            
            # Запрос к OpenAI
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            print(f"✅ AI ответ получен (модель: {model})")
            
            return answer, model
            
        except Exception as e:
            print(f"❌ Ошибка AI: {e}")
            return None, None
    
    async def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Транскрибировать аудио в текст (Whisper)
        
        Args:
            audio_file_path: Путь к аудио файлу
            
        Returns:
            Транскрибированный текст или None
        """
        try:
            with open(audio_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="hy"  # Армянский по умолчанию
                )
            
            print(f"✅ Аудио транскрибировано: {transcript.text[:50]}...")
            return transcript.text
            
        except Exception as e:
            print(f"❌ Ошибка транскрипции: {e}")
            return None
