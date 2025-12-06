"""
Instagram клиент (заглушка для будущей реализации)
Требует: instagrapi (добавить в requirements когда будет API)
"""


class InstagramClient:
    """Клиент для Instagram"""
    
    def __init__(self, username: str, password: str):
        """
        Инициализация клиента
        
        Args:
            username: Instagram username
            password: Instagram password
        """
        self.username = username
        self.password = password
        # TODO: Инициализация instagrapi когда будет API
        print(f"⚠️ Instagram клиент создан (заглушка)")
    
    async def post(self, caption: str, image_path: str = None):
        """
        Публикация поста
        
        Args:
            caption: Текст поста
            image_path: Путь к изображению
            
        Returns:
            Результат публикации
        """
        # TODO: Реализовать когда будет API
        raise NotImplementedError(
            "Instagram API не реализован. "
            "Установите instagrapi и добавьте реализацию."
        )
