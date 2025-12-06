"""
Генератор контента для различных платформ
"""
from typing import Optional, Dict
from openai import OpenAI


class ContentGenerator:
    """Генератор контента через OpenAI"""
    
    def __init__(self, api_key: str):
        """
        Инициализация генератора
        
        Args:
            api_key: OpenAI API ключ
        """
        self.client = OpenAI(api_key=api_key)
    
    async def generate_blog_post(
        self,
        topic: str,
        language: str = 'hy',
        length: str = 'medium'
    ) -> Optional[str]:
        """
        Генерация статьи для блога
        
        Args:
            topic: Тема статьи
            language: Язык (hy, ru, en)
            length: Длина (short, medium, long)
            
        Returns:
            Сгенерированная статья
        """
        try:
            length_tokens = {
                'short': 300,
                'medium': 600,
                'long': 1000
            }
            
            prompts = {
                'hy': f"Գրիր մանրամասն հոդված այս թեմայով: {topic}\n\nՀոդվածը պետք է լինի տեղեկատվական, հետաքրքիր և լավ կառուցված։",
                'ru': f"Напиши подробную статью на тему: {topic}\n\nСтатья должна быть информативной, интересной и хорошо структурированной.",
                'en': f"Write a detailed blog post about: {topic}\n\nThe post should be informative, engaging and well-structured."
            }
            
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a professional content writer."},
                    {"role": "user", "content": prompts.get(language, prompts['en'])}
                ],
                temperature=0.8,
                max_tokens=length_tokens.get(length, 600)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Ошибка генерации статьи: {e}")
            return None
    
    async def generate_social_post(
        self,
        topic: str,
        platform: str = 'instagram',
        language: str = 'hy'
    ) -> Optional[Dict[str, str]]:
        """
        Генерация поста для соцсетей
        
        Args:
            topic: Тема поста
            platform: Платформа (instagram, youtube, tiktok, facebook)
            language: Язык
            
        Returns:
            Dict с текстом и хештегами
        """
        try:
            platform_specs = {
                'instagram': {
                    'hy': 'Գրիր գրավիչ Instagram պոստ',
                    'ru': 'Напиши привлекательный Instagram пост',
                    'en': 'Write an engaging Instagram post'
                },
                'youtube': {
                    'hy': 'Գրիր YouTube վիդեոյի նկարագրություն',
                    'ru': 'Напиши описание для YouTube видео',
                    'en': 'Write a YouTube video description'
                },
                'tiktok': {
                    'hy': 'Գրիր կարճ TikTok պոստ',
                    'ru': 'Напиши короткий TikTok пост',
                    'en': 'Write a short TikTok post'
                },
                'facebook': {
                    'hy': 'Գրիր Facebook պոստ',
                    'ru': 'Напиши Facebook пост',
                    'en': 'Write a Facebook post'
                }
            }
            
            instruction = platform_specs.get(platform, platform_specs['instagram']).get(language, 'Write a social media post')
            
            prompt = f"{instruction} на тему: {topic}\n\nВключи релевантные хештеги."
            
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a social media content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            # Разделяем текст и хештеги
            lines = content.split('\n')
            text_lines = []
            hashtags = []
            
            for line in lines:
                if '#' in line:
                    hashtags.extend([tag.strip() for tag in line.split() if tag.startswith('#')])
                else:
                    text_lines.append(line)
            
            return {
                'text': '\n'.join(text_lines).strip(),
                'hashtags': ' '.join(hashtags) if hashtags else ''
            }
            
        except Exception as e:
            print(f"❌ Ошибка генерации поста: {e}")
            return None
    
    async def generate_video_script(
        self,
        topic: str,
        duration: int = 60,
        language: str = 'hy'
    ) -> Optional[str]:
        """
        Генерация сценария для видео
        
        Args:
            topic: Тема видео
            duration: Длительность в секундах
            language: Язык
            
        Returns:
            Сценарий видео
        """
        try:
            prompts = {
                'hy': f"Ստեղծիր {duration} վայրկյանանոց վիդեո սցենար այս թեմայով: {topic}\n\nՆշիր ժամանակային կոդերը և տեսողական էլեմենտները։",
                'ru': f"Создай сценарий для {duration}-секундного видео на тему: {topic}\n\nУкажи таймкоды и визуальные элементы.",
                'en': f"Create a {duration}-second video script about: {topic}\n\nInclude timecodes and visual elements."
            }
            
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a professional video scriptwriter."},
                    {"role": "user", "content": prompts.get(language, prompts['en'])}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Ошибка генерации сценария: {e}")
            return None
    
    async def generate_ad_copy(
        self,
        product: str,
        target_audience: str,
        language: str = 'hy'
    ) -> Optional[str]:
        """
        Генерация рекламного текста
        
        Args:
            product: Продукт/услуга
            target_audience: Целевая аудитория
            language: Язык
            
        Returns:
            Рекламный текст
        """
        try:
            prompts = {
                'hy': f"Ստեղծիր գրավիչ գովազդային տեքստ\n\nՊրոդուկտ: {product}\nԱուդիտորիա: {target_audience}\n\nՏեքստը պետք է լինի համոզիչ և մոտիվացնող։",
                'ru': f"Создай привлекательный рекламный текст\n\nПродукт: {product}\nАудитория: {target_audience}\n\nТекст должен быть убедительным и мотивирующим.",
                'en': f"Create compelling ad copy\n\nProduct: {product}\nTarget audience: {target_audience}\n\nThe copy should be persuasive and motivating."
            }
            
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are an expert copywriter."},
                    {"role": "user", "content": prompts.get(language, prompts['en'])}
                ],
                temperature=0.9,
                max_tokens=400
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Ошибка генерации рекламы: {e}")
            return None
