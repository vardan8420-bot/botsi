"""
TikTok клиент (заглушка для будущей реализации)
Требует: TikTokApi (добавить в requirements когда будет API)
"""


class TikTokClient:
    """Клиент для TikTok"""
    
    def __init__(self, session_id: str):
        """
        Инициализация клиента
        
        Args:
            session_id: TikTok session ID
        """
        self.session_id = session_id
        # TODO: Инициализация TikTok API когда будет session
        print(f"⚠️ TikTok клиент создан (заглушка)")
    
    async def post(
        self,
        caption: str,
        video_path: str,
        hashtags: list = None
    ):
        """
        Публикация видео
        
        Args:
            caption: Описание видео
            video_path: Путь к видео
            hashtags: Хештеги
            
        Returns:
            Результат публикации
        """
        # TODO: Реализовать когда будет API
        raise NotImplementedError(
            "TikTok API не реализован. "
            "Установите TikTokApi и добавьте реализацию."
        )
