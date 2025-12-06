# -*- coding: utf-8 -*-
"""
SMM и Маркетинг сервис - идеальный маркетолог
"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json


class SMMMarketingService:
    """Сервис для SMM и маркетинга"""
    
    def __init__(self, openai_client):
        """
        Инициализация сервиса
        
        Args:
            openai_client: OpenAI клиент
        """
        self.openai = openai_client
        print("✅ SMM & Marketing сервис инициализирован")
    
    async def generate_content_plan(
        self,
        niche: str,
        platform: str,
        days: int = 7,
        language: str = 'ru'
    ) -> Dict:
        """
        Генерация контент-плана
        
        Args:
            niche: Ниша/тематика
            platform: Платформа (instagram, facebook, telegram)
            days: Количество дней
            language: Язык
            
        Returns:
            Контент-план
        """
        try:
            prompt = f"""Создай детальный контент-план для {platform} на {days} дней.

Ниша: {niche}
Язык: {language}

Для каждого дня укажи:
1. Тему поста
2. Тип контента (фото/видео/карусель/текст)
3. Краткое описание
4. Лучшее время публикации
5. Хештеги (5-10 штук)
6. Call-to-action

Формат: JSON с ключами: day, theme, type, description, time, hashtags, cta"""

            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ты профессиональный SMM-менеджер и контент-стратег."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            
            return {
                'success': True,
                'niche': niche,
                'platform': platform,
                'days': days,
                'plan': content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка генерации: {str(e)}'
            }
    
    async def analyze_target_audience(
        self,
        product: str,
        language: str = 'ru'
    ) -> Dict:
        """
        Анализ целевой аудитории
        
        Args:
            product: Продукт/услуга
            language: Язык
            
        Returns:
            Анализ ЦА
        """
        try:
            prompt = f"""Проведи глубокий анализ целевой аудитории для: {product}

Укажи:
1. Демография (возраст, пол, локация, доход)
2. Психография (интересы, ценности, образ жизни)
3. Боли и проблемы
4. Желания и мечты
5. Где они находятся (платформы, сообщества)
6. Как с ними говорить (tone of voice)
7. Что их мотивирует к покупке

Будь максимально конкретным и практичным."""

            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ты эксперт по маркетингу и анализу целевой аудитории."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return {
                'success': True,
                'product': product,
                'analysis': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}'
            }
    
    async def create_sales_funnel(
        self,
        product: str,
        language: str = 'ru'
    ) -> Dict:
        """
        Создание воронки продаж
        
        Args:
            product: Продукт/услуга
            language: Язык
            
        Returns:
            Воронка продаж
        """
        try:
            prompt = f"""Создай детальную воронку продаж для: {product}

Опиши каждый этап:
1. AWARENESS (Осведомленность)
   - Как привлечь внимание
   - Каналы трафика
   - Контент для этого этапа

2. INTEREST (Интерес)
   - Как заинтересовать
   - Лид-магниты
   - Контент

3. DESIRE (Желание)
   - Как создать желание купить
   - Триггеры
   - Доказательства

4. ACTION (Действие)
   - Как подтолкнуть к покупке
   - Офферы
   - CTA

5. RETENTION (Удержание)
   - Как удержать клиента
   - Программы лояльности

Для каждого этапа дай конкретные действия и примеры."""

            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ты эксперт по маркетинговым воронкам и продажам."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return {
                'success': True,
                'product': product,
                'funnel': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}'
            }
    
    async def generate_selling_copy(
        self,
        product: str,
        format_type: str = 'post',
        language: str = 'ru'
    ) -> Dict:
        """
        Генерация продающего текста
        
        Args:
            product: Продукт/услуга
            format_type: Формат (post, email, ad, landing)
            language: Язык
            
        Returns:
            Продающий текст
        """
        try:
            formats = {
                'post': 'пост для соцсетей',
                'email': 'email рассылку',
                'ad': 'рекламное объявление',
                'landing': 'текст для лендинга'
            }
            
            format_name = formats.get(format_type, 'текст')
            
            prompt = f"""Напиши продающий {format_name} для: {product}

Используй формулу AIDA:
- Attention (Внимание) - цепляющий заголовок
- Interest (Интерес) - заинтересуй проблемой/решением
- Desire (Желание) - покажи выгоды и результат
- Action (Действие) - четкий призыв к действию

Требования:
- Эмоциональный и убедительный
- Конкретные выгоды
- Социальные доказательства
- Срочность и дефицит
- Сильный CTA

Язык: {language}"""

            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ты топовый копирайтер и маркетолог. Пишешь тексты которые продают."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            return {
                'success': True,
                'product': product,
                'format': format_type,
                'copy': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}'
            }
    
    async def generate_hashtags(
        self,
        topic: str,
        count: int = 30,
        language: str = 'ru'
    ) -> Dict:
        """
        Генерация хештегов
        
        Args:
            topic: Тема
            count: Количество хештегов
            language: Язык
            
        Returns:
            Список хештегов
        """
        try:
            prompt = f"""Сгенерируй {count} эффективных хештегов для темы: {topic}

Требования:
- Микс популярных и нишевых
- Разная частотность (высокая, средняя, низкая)
- Релевантные теме
- На языке: {language}

Раздели на категории:
1. Популярные (высокая конкуренция)
2. Средние (средняя конкуренция)
3. Нишевые (низкая конкуренция)"""

            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты эксперт по SMM и хештегам."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return {
                'success': True,
                'topic': topic,
                'hashtags': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}'
            }
    
    async def analyze_competitor(
        self,
        competitor: str,
        your_product: str,
        language: str = 'ru'
    ) -> Dict:
        """
        Анализ конкурента
        
        Args:
            competitor: Конкурент
            your_product: Ваш продукт
            language: Язык
            
        Returns:
            Анализ конкурента
        """
        try:
            prompt = f"""Проведи конкурентный анализ:

Конкурент: {competitor}
Наш продукт: {your_product}

Проанализируй:
1. Их сильные стороны
2. Их слабые стороны
3. Их стратегия контента
4. Их ценообразование
5. Их УТП (уникальное торговое предложение)
6. Что мы можем сделать лучше
7. Как выделиться на их фоне

Дай конкретные рекомендации для победы."""

            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ты эксперт по конкурентному анализу и маркетинговой стратегии."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return {
                'success': True,
                'competitor': competitor,
                'analysis': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}'
            }
