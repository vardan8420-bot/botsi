"""
Facebook клиент (заглушка для будущей реализации)
Требует: facebook-sdk (добавить в requirements когда будет API)
"""


class FacebookClient:
    """Клиент для Facebook"""
    
    def __init__(self, access_token: str):
        """
        Инициализация клиента
        
        Args:
            access_token: Facebook access token
        """
        self.access_token = access_token
        # TODO: Инициализация Facebook API когда будет токен
        print(f"⚠️ Facebook клиент создан (заглушка)")
    
    async def post(self, message: str, image_path: str = None):
        """
        Публикация поста
        
        Args:
            message: Текст поста
            image_path: Путь к изображению
            
        Returns:
            Результат публикации
        """
        # TODO: Реализовать когда будет API
        raise NotImplementedError(
            "Facebook API не реализован. "
            "Установите facebook-sdk и добавьте реализацию."
        )
