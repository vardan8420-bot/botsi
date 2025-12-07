"""
YouTube Analyst - Сервис для анализа видео контента
"""
from typing import Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re


class YouTubeAnalystService:
    """Сервис для анализа YouTube видео"""
    
    def __init__(self, openai_client):
        self.openai = openai_client
        print("✅ YouTube Analyst (Видео Аналитик) инициализирован")

    def _get_video_id(self, url: str) -> Optional[str]:
        """Извлекает ID видео из ссылки"""
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                p = parse_qs(parsed_url.query)
                return p['v'][0]
            if parsed_url.path[:7] == '/embed/':
                return parsed_url.path.split('/')[2]
            if parsed_url.path[:3] == '/v/':
                return parsed_url.path.split('/')[2]
        return None

    async def get_video_summary(self, url: str, language: str = 'ru') -> Dict:
        """
        Получает транскрипцию и делает саммари видео
        """
        try:
            video_id = self._get_video_id(url)
            if not video_id:
                return {"success": False, "error": "Некорректная ссылка на YouTube"}

            # Получаем субтитры (пробуем разные языки)
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru', 'en', 'hy'])
            except Exception:
                # Если нет субтитров, пробуем авто-субтитры
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id).find_generated_transcript(['ru', 'en']).fetch()
                except Exception as e:
                    return {"success": False, "error": f"Не удалось получить субтитры: {str(e)}"}

            # Собираем текст
            full_text = " ".join([t['text'] for t in transcript_list])
            
            # Обрезаем, если слишком длинный (GPT лимит)
            if len(full_text) > 15000:
                full_text = full_text[:15000] + "..."

            # Анализ через GPT
            prompt = f"""Проанализируй этот текст из YouTube видео и сделай подробное саммари.

Текст видео:
{full_text}

Задача:
1. 📝 **Краткое содержание** (в 3-5 предложениях).
2. 🔑 **Ключевые идеи/инсайты** (списком).
3. 💡 **Практические советы** (если есть).
4. 🎯 **Для кого это видео?** (целевая аудитория).
5. 📱 **Пост для соцсетей** (напиши короткий пост об этом видео).

Язык ответа: {language}
"""
            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ты профессиональный контент-аналитик. Ты умеешь выделять суть из видео."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            summary = response.choices[0].message.content
            
            return {
                "success": True,
                "title": f"Анализ видео {video_id}",
                "summary": summary,
                "full_text_preview": full_text[:200]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
