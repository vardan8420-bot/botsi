"""
Менеджер социальных сетей с реальными API
"""
from typing import Optional, Dict
import os


class SocialMediaManager:
    """Менеджер для автопостинга в соцсети"""
    
    def __init__(
        self,
        instagram_username: Optional[str] = None,
        instagram_password: Optional[str] = None,
        facebook_token: Optional[str] = None
    ):
        """
        Инициализация менеджера
        
        Args:
            instagram_username: Instagram логин
            instagram_password: Instagram пароль
            facebook_token: Facebook access token
        """
        self.instagram_available = False
        self.facebook_available = False
        
        # Instagram (через instagrapi)
        if instagram_username and instagram_password:
            try:
                from instagrapi import Client
                self.instagram_client = Client()
                self.instagram_client.login(instagram_username, instagram_password)
                self.instagram_available = True
                print("✅ Instagram подключен")
            except Exception as e:
                print(f"⚠️ Instagram недоступен: {e}")
        else:
            print("⚠️ Instagram: нужны INSTAGRAM_USERNAME и INSTAGRAM_PASSWORD")
        
        # Facebook (через Graph API)
        if facebook_token:
            self.facebook_token = facebook_token
            self.facebook_available = True
            print("✅ Facebook подключен")
        else:
            print("⚠️ Facebook: нужен FACEBOOK_ACCESS_TOKEN")
    
    async def post_instagram(
        self,
        caption: str,
        image_path: Optional[str] = None
    ) -> Dict:
        """
        Опубликовать в Instagram
        
        Args:
            caption: Текст поста
            image_path: Путь к изображению (опционально)
            
        Returns:
            Результат публикации
        """
        if not self.instagram_available:
            return {
                'success': False,
                'error': 'Instagram недоступен. Добавьте учетные данные.'
            }
        
        try:
            if image_path:
                # Пост с фото
                media = self.instagram_client.photo_upload(
                    image_path,
                    caption=caption
                )
            else:
                return {
                    'success': False,
                    'error': 'Для Instagram нужно изображение'
                }
            
            return {
                'success': True,
                'platform': 'Instagram',
                'post_id': media.pk,
                'url': f"https://instagram.com/p/{media.code}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка Instagram: {str(e)}'
            }
    
    async def post_facebook(self, message: str, link: Optional[str] = None) -> Dict:
        """
        Опубликовать в Facebook
        
        Args:
            message: Текст поста
            link: Ссылка (опционально)
            
        Returns:
            Результат публикации
        """
        if not self.facebook_available:
            return {
                'success': False,
                'error': 'Facebook недоступен. Добавьте FACEBOOK_ACCESS_TOKEN.'
            }
        
        try:
            import requests
            
            url = f"https://graph.facebook.com/v18.0/me/feed"
            
            params = {
                'message': message,
                'access_token': self.facebook_token
            }
            
            if link:
                params['link'] = link
            
            response = requests.post(url, params=params)
            data = response.json()
            
            if 'id' in data:
                return {
                    'success': True,
                    'platform': 'Facebook',
                    'post_id': data['id'],
                    'url': f"https://facebook.com/{data['id']}"
                }
            else:
                return {
                    'success': False,
                    'error': data.get('error', {}).get('message', 'Unknown error')
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка Facebook: {str(e)}'
            }
    
    def get_status(self) -> Dict:
        """
        Получить статус подключений
        
        Returns:
            Статус всех платформ
        """
        return {
            'instagram': self.instagram_available,
            'facebook': self.facebook_available,
            'available_platforms': [
                p for p, available in [
                    ('Instagram', self.instagram_available),
                    ('Facebook', self.facebook_available)
                ] if available
            ]
        }
