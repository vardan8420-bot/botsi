"""
YouTube клиент (заглушка для будущей реализации)
Требует: google-api-python-client (добавить в requirements когда будет API)
"""


class YouTubeClient:
    """Клиент для YouTube"""
    
    def __init__(self, api_key: str):
        """
        Инициализация клиента
        
        Args:
            api_key: YouTube API ключ
        """
        self.api_key = api_key
        # TODO: Инициализация YouTube API когда будет ключ
        print(f"⚠️ YouTube клиент создан (заглушка)")
    
    async def upload(
        self,
        title: str,
        description: str,
        video_path: str,
        tags: list = None
    ):
        """
        Загрузка видео
        
        Args:
            title: Название видео
            description: Описание
            video_path: Путь к видео
            tags: Теги
            
        Returns:
            Результат загрузки
        """
        # TODO: Реализовать когда будет API
        raise NotImplementedError(
            "YouTube API не реализован. "
            "Установите google-api-python-client и добавьте реализацию."
        )
