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
        """
        self.instagram_available = False
        self.facebook_available = False
        
        # Instagram (через instagrapi)
        try:
            from instagrapi import Client
            self.instagram_client = Client()
            
            session_id = os.getenv('INSTAGRAM_SESSION_ID')
            
            # 1. Сначала пробуем Session ID (самый надежный способ)
            if session_id:
                try:
                    self.instagram_client.login_by_sessionid(session_id)
                    self.instagram_available = True
                    # Узнаем, кто мы
                    try:
                        self.my_info = self.instagram_client.account_info()
                        self.my_username = self.my_info.username
                        print(f"✅ Instagram подключен как: {self.my_username}")
                    except:
                        self.my_username = "Unknown"
                        
                    print("✅ Instagram подключен (через Session ID)")
                except Exception as e:
                    print(f"⚠️ Ошибка входа по Session ID: {e}")
            
            # 2. Если не вышло - пробуем Логин/Пароль
            if not self.instagram_available and instagram_username and instagram_password:
                try:
                    self.instagram_client.login(instagram_username, instagram_password)
                    self.instagram_available = True
                    
                    # Узнаем, кто мы
                    try:
                        self.my_info = self.instagram_client.account_info()
                        self.my_username = self.my_info.username
                    except:
                        self.my_username = "Unknown"

                    print(f"✅ Instagram подключен (Логин/Пароль) как: {self.my_username}")
                except Exception as e:
                    print(f"⚠️ Instagram недоступен (Логин/Пароль): {e}")
                    
            if not self.instagram_available:
                print("⚠️ Instagram не подключен. Укажите INSTAGRAM_SESSION_ID или Логин/Пароль")
                
        except Exception as e:
            print(f"⚠️ Ошибка инициализации Instagram: {e}")
        
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
    
    async def get_my_posts(self, limit: int = 5) -> Dict:
        """
        Получить последние посты своего аккаунта для анализа
        """
        if not self.instagram_available:
            return {"success": False, "error": "Instagram не подключен"}
            
        try:
            # Получаем ID пользователя
            user_id = self.instagram_client.user_id_from_username(self.my_username)
            # Получаем медиа
            medias = self.instagram_client.user_medias(user_id, amount=limit)
            
            posts_data = []
            for media in medias:
                posts_data.append({
                    "id": media.pk,
                    "caption": media.caption_text,
                    "likes": media.like_count,
                    "comments": media.comment_count,
                    "type": media.media_type, # 1=Photo, 2=Video, 8=Album
                    "url": f"https://instagram.com/p/{media.code}"
                })
                
            return {
                "success": True, 
                "username": self.my_username,
                "posts": posts_data
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def update_profile(self, biography: str = None, full_name: str = None, external_url: str = None) -> Dict:
        """
        Обновление информации профиля (Био, Имя, Сайт)
        """
        if not self.instagram_available:
            return {"success": False, "error": "Нет подключения к Instagram"}
            
        try:
            # Сначала получаем текущие данные, чтобы не стереть лишнее
            current_info = self.instagram_client.account_info()
            
            new_biography = biography if biography is not None else current_info.biography
            new_full_name = full_name if full_name is not None else current_info.full_name
            new_external_url = external_url if external_url is not None else current_info.external_url
            
            self.instagram_client.account_edit(
                biography=new_biography,
                first_name=new_full_name,
                external_url=new_external_url
            )
            return {"success": True, "message": "Профиль успешно обновлен!"}
        except Exception as e:
            return {"success": False, "error": f"Ошибка обновления профиля: {str(e)}"}

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
