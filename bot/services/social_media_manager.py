"""
Менеджер соцсетей с fallback механизмом
Работает даже если API ключи отсутствуют
"""
from typing import Optional, Dict
import logging


class SocialMediaManager:
    """Менеджер публикаций в соцсети с graceful degradation"""
    
    def __init__(self, config):
        """
        Инициализация менеджера
        
        Args:
            config: Объект конфигурации
        """
        self.config = config
        self.instagram = None
        self.youtube = None
        self.tiktok = None
        self.facebook = None
        
        # Инициализация доступных платформ
        self._init_platforms()
    
    def _init_platforms(self):
        """Инициализация платформ (только если есть API ключи)"""
        
        # Instagram
        if self.config.INSTAGRAM_USERNAME and self.config.INSTAGRAM_PASSWORD:
            try:
                from .platforms.instagram_client import InstagramClient
                self.instagram = InstagramClient(
                    self.config.INSTAGRAM_USERNAME,
                    self.config.INSTAGRAM_PASSWORD
                )
                print("✅ Instagram клиент инициализирован")
            except Exception as e:
                print(f"⚠️ Instagram недоступен: {e}")
        
        # YouTube
        if self.config.YOUTUBE_API_KEY:
            try:
                from .platforms.youtube_client import YouTubeClient
                self.youtube = YouTubeClient(self.config.YOUTUBE_API_KEY)
                print("✅ YouTube клиент инициализирован")
            except Exception as e:
                print(f"⚠️ YouTube недоступен: {e}")
        
        # TikTok
        if self.config.TIKTOK_SESSION_ID:
            try:
                from .platforms.tiktok_client import TikTokClient
                self.tiktok = TikTokClient(self.config.TIKTOK_SESSION_ID)
                print("✅ TikTok клиент инициализирован")
            except Exception as e:
                print(f"⚠️ TikTok недоступен: {e}")
        
        # Facebook
        if self.config.FACEBOOK_ACCESS_TOKEN:
            try:
                from .platforms.facebook_client import FacebookClient
                self.facebook = FacebookClient(self.config.FACEBOOK_ACCESS_TOKEN)
                print("✅ Facebook клиент инициализирован")
            except Exception as e:
                print(f"⚠️ Facebook недоступен: {e}")
    
    def get_available_platforms(self) -> list:
        """Получить список доступных платформ"""
        platforms = []
        if self.instagram:
            platforms.append('instagram')
        if self.youtube:
            platforms.append('youtube')
        if self.tiktok:
            platforms.append('tiktok')
        if self.facebook:
            platforms.append('facebook')
        return platforms
    
    async def post_to_instagram(
        self,
        caption: str,
        image_path: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Публикация в Instagram
        
        Args:
            caption: Текст поста
            image_path: Путь к изображению
            
        Returns:
            Результат публикации
        """
        if not self.instagram:
            return {
                'success': False,
                'error': 'Instagram API не настроен. Добавьте INSTAGRAM_USERNAME и INSTAGRAM_PASSWORD.'
            }
        
        try:
            result = await self.instagram.post(caption, image_path)
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def post_to_youtube(
        self,
        title: str,
        description: str,
        video_path: str,
        tags: list = None
    ) -> Dict[str, any]:
        """
        Публикация на YouTube
        
        Args:
            title: Название видео
            description: Описание
            video_path: Путь к видео
            tags: Теги
            
        Returns:
            Результат публикации
        """
        if not self.youtube:
            return {
                'success': False,
                'error': 'YouTube API не настроен. Добавьте YOUTUBE_API_KEY.'
            }
        
        try:
            result = await self.youtube.upload(title, description, video_path, tags)
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def post_to_tiktok(
        self,
        caption: str,
        video_path: str,
        hashtags: list = None
    ) -> Dict[str, any]:
        """
        Публикация в TikTok
        
        Args:
            caption: Описание видео
            video_path: Путь к видео
            hashtags: Хештеги
            
        Returns:
            Результат публикации
        """
        if not self.tiktok:
            return {
                'success': False,
                'error': 'TikTok API не настроен. Добавьте TIKTOK_SESSION_ID.'
            }
        
        try:
            result = await self.tiktok.post(caption, video_path, hashtags)
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def post_to_facebook(
        self,
        message: str,
        image_path: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Публикация в Facebook
        
        Args:
            message: Текст поста
            image_path: Путь к изображению
            
        Returns:
            Результат публикации
        """
        if not self.facebook:
            return {
                'success': False,
                'error': 'Facebook API не настроен. Добавьте FACEBOOK_ACCESS_TOKEN.'
            }
        
        try:
            result = await self.facebook.post(message, image_path)
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def post_to_all(
        self,
        content: Dict[str, str],
        media_path: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Публикация во все доступные платформы
        
        Args:
            content: Контент для каждой платформы
            media_path: Путь к медиа файлу
            
        Returns:
            Результаты для каждой платформы
        """
        results = {}
        
        if self.instagram and 'instagram' in content:
            results['instagram'] = await self.post_to_instagram(
                content['instagram'],
                media_path
            )
        
        if self.facebook and 'facebook' in content:
            results['facebook'] = await self.post_to_facebook(
                content['facebook'],
                media_path
            )
        
        # YouTube и TikTok требуют видео
        if media_path and media_path.endswith(('.mp4', '.mov', '.avi')):
            if self.youtube and 'youtube' in content:
                results['youtube'] = await self.post_to_youtube(
                    content.get('youtube_title', 'Video'),
                    content['youtube'],
                    media_path
                )
            
            if self.tiktok and 'tiktok' in content:
                results['tiktok'] = await self.post_to_tiktok(
                    content['tiktok'],
                    media_path
                )
        
        return results
