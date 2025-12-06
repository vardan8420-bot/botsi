"""
Mind Sync - Система адаптации под мышление пользователя
"""
from typing import Dict, List, Optional
import json


class MindSyncService:
    """Сервис для синхронизации с мышлением пользователя"""
    
    def __init__(self, openai_client, memory_service):
        """
        Инициализация
        
        Args:
            openai_client: OpenAI клиент
            memory_service: Сервис памяти (для сохранения профиля)
        """
        self.client = openai_client
        self.memory = memory_service
        print("✅ Mind Sync (Адаптация мышления) активирована")
        
    async def analyze_and_update_profile(self, user_id: int, history: List[Dict]) -> str:
        """
        Анализ истории и обновление профиля мышления
        
        Args:
            user_id: ID пользователя
            history: История сообщений
            
        Returns:
            Обновленный профиль
        """
        try:
            # Берем последние 10 сообщений для анализа
            recent_chat = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in history[-10:]])
            
            prompt = f"""Проанализируй стиль общения и мышления пользователя на основе диалога.

Диалог:
{recent_chat}

Составь краткий "Психологический профиль" для AI, чтобы лучше отвечать этому пользователю.
Ответь ТОЛЬКО профилем в формате списка инструкций.

Анализируй:
1. Как он формулирует мысли (четко/хаотично/абстрактно)?
2. Что он ценит (код/теорию/краткость/общение)?
3. Как его "пинать" (мягко направлять или давать жесткие инструкции)?
4. Какой тон ему нравится?

Пример ответа:
- Пользователь ценит конкретику и готовый код.
- Не любит долгие вступления.
- Пишет мысли потоком, нужно их структурировать за него.
- Обращаться как к коллеге-эксперту."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты психолог-аналитик."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            profile = response.choices[0].message.content
            
            # Сохраняем в долгосрочную память
            await self.memory.remember(
                user_id=user_id,
                fact=f"MIND_PROFILE: {profile}",
                category="mind_profile"
            )
            
            return profile
            
        except Exception as e:
            print(f"⚠️ Ошибка Mind Sync: {e}")
            return ""

    async def get_adaptive_instruction(self, user_id: int) -> str:
        """
        Получить инструкцию для адаптации под пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Инструкция для системного промпта
        """
        # Пытаемся найти последний профиль в памяти
        result = await self.memory.recall(user_id, category="mind_profile", limit=1)
        
        if result['success'] and result['memories']:
            profile = result['memories'][0]['fact'].replace("MIND_PROFILE: ", "")
            return f"\n\n⚡ АДАПТАЦИЯ ПОД ПОЛЬЗОВАТЕЛЯ:\n{profile}\nСледуй этим правилам неукоснительно!"
        
        return ""
