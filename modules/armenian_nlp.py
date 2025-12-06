"""
Обработка армянского языка
- Определение языка
- Проверка транслита
"""
import re
from typing import List


class ArmenianNLP:
    """Обработка армянского языка"""
    
    # Армянские буквы (Unicode диапазон)
    ARMENIAN_PATTERN = re.compile(r'[\u0530-\u058F]')
    
    # Паттерны транслита
    TRANSLIT_PATTERNS = [
        r'\b(voghchuyn|barev|inchpes|shat|lav|yes|du|inch|vor|ayd|ays|ayn)\b',
        r'\b(mer|ner|dzer|mnac|gnac|el|gnal|grel|karox|petq)\b',
        r'\b(ha|vo|che|ara|lav|shat|shnorhakalutyun)\b',
    ]
    
    def __init__(self):
        """Инициализация NLP обработчика"""
        self.translit_pattern = re.compile(
            '|'.join(self.TRANSLIT_PATTERNS),
            re.IGNORECASE
        )
    
    def detect_language(self, text: str) -> str:
        """
        Определяет язык текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Код языка: 'hy', 'ru', 'en', 'hy-translit'
        """
        text_lower = text.lower().strip()
        
        # Проверка на армянский (Unicode)
        if self.ARMENIAN_PATTERN.search(text):
            return 'hy'
        
        # Проверка на транслит
        if self.is_translit(text_lower):
            return 'hy-translit'
        
        # Простая проверка на русский (кириллица)
        if re.search(r'[а-яё]', text_lower, re.IGNORECASE):
            return 'ru'
        
        # Проверка на английский
        if re.search(r'[a-z]', text_lower):
            return 'en'
        
        # По умолчанию армянский
        return 'hy'
    
    def is_translit(self, text: str) -> bool:
        """
        Проверяет является ли текст транслитом
        
        Args:
            text: Текст для проверки
            
        Returns:
            True если это транслит
        """
        # Проверка на наличие армянских слов в транслите
        common_translit_words = [
            'voghchuyn', 'barev', 'inchpes', 'shat', 'lav',
            'yes', 'du', 'inch', 'vor', 'ayd', 'ays', 'ayn',
            'mer', 'ner', 'dzer', 'mnac', 'gnac', 'el',
            'gnal', 'grel', 'karox', 'petq', 'ha', 'vo',
            'che', 'ara', 'shnorhakalutyun'
        ]
        
        text_lower = text.lower()
        
        # Проверка на наличие транслит слов
        for word in common_translit_words:
            if word in text_lower:
                return True
        
        # Проверка по паттернам
        if self.translit_pattern.search(text_lower):
            return True
        
        return False
    
    def extract_armenian_words(self, text: str) -> List[str]:
        """
        Извлекает армянские слова из текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Список армянских слов
        """
        words = re.findall(r'[\u0530-\u058F]+', text)
        return words

