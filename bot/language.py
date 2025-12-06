"""
Определение языка и работа с армянским
"""
import re


class LanguageDetector:
    """Определение языка сообщения"""
    
    # Армянские символы Unicode
    ARMENIAN_PATTERN = re.compile(r'[\u0530-\u058F\u0590-\u05FF]+')
    
    # Кириллица (русский)
    CYRILLIC_PATTERN = re.compile(r'[\u0400-\u04FF]+')
    
    # Латиница
    LATIN_PATTERN = re.compile(r'[a-zA-Z]+')
    
    # Транслит паттерны (латиница с армянскими словами)
    TRANSLIT_KEYWORDS = [
        'barev', 'vonc', 'es', 'inch', 'ka', 'em', 'eq',
        'vor', 'aysor', 'vagh', 'lav', 'shat', 'mer',
        'du', 'yes', 'menq', 'duq', 'nranq'
    ]
    
    @classmethod
    def detect(cls, text: str) -> str:
        """
        Определить язык текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Код языка: 'hy', 'ru', 'en', 'hy-translit'
        """
        if not text:
            return 'en'
        
        text_lower = text.lower()
        
        # Проверка на армянский
        if cls.ARMENIAN_PATTERN.search(text):
            return 'hy'
        
        # Проверка на русский
        if cls.CYRILLIC_PATTERN.search(text):
            return 'ru'
        
        # Проверка на транслит
        for keyword in cls.TRANSLIT_KEYWORDS:
            if keyword in text_lower:
                return 'hy-translit'
        
        # По умолчанию английский
        return 'en'
    
    @staticmethod
    def is_armenian(text: str) -> bool:
        """Проверить является ли текст армянским"""
        return bool(re.search(r'[\u0530-\u058F]+', text))
    
    @staticmethod
    def is_russian(text: str) -> bool:
        """Проверить является ли текст русским"""
        return bool(re.search(r'[\u0400-\u04FF]+', text))


class TranslitConverter:
    """Конвертер транслита в армянский"""
    
    # Базовый словарь транслитерации
    TRANSLIT_MAP = {
        # Гласные
        'a': 'ա', 'e': 'ե', 'i': 'ի', 'o': 'ո', 'u': 'ու',
        
        # Согласные
        'b': 'բ', 'g': 'գ', 'd': 'դ', 'z': 'զ', 't': 't',
        'zh': 'ժ', 'l': 'լ', 'kh': 'խ', 'ts': 'ծ', 'k': 'կ',
        'h': 'հ', 'dz': 'ձ', 'gh': 'ղ', 'ch': 'ճ', 'm': 'մ',
        'y': 'յ', 'n': 'ն', 'sh': 'շ', 'vo': 'ո', 'ch': 'չ',
        'p': 'պ', 'j': 'ջ', 'r': 'ռ', 's': 'ս', 'v': 'վ',
        'f': 'ֆ', 'q': 'ք', 'ev': 'և',
        
        # Специальные комбинации
        'ye': 'ե', 'yo': 'յո', 'yu': 'յու', 'ya': 'յա',
    }
    
    # Популярные слова
    WORD_MAP = {
        'barev': 'բարև',
        'vonc': 'ո՞նց',
        'es': 'ես',
        'inch': 'ինչ',
        'ka': 'կա',
        'em': 'եմ',
        'eq': 'եք',
        'vor': 'որ',
        'aysor': 'այսօր',
        'vagh': 'վաղ',
        'lav': 'լավ',
        'shat': 'շատ',
        'mer': 'մեր',
        'du': 'դու',
        'yes': 'ես',
        'menq': 'մենք',
        'duq': 'դուք',
        'nranq': 'նրանք',
    }
    
    @classmethod
    def convert(cls, text: str) -> str:
        """
        Конвертировать транслит в армянский
        
        Args:
            text: Текст на транслите
            
        Returns:
            Текст на армянском (если возможно)
        """
        if not text:
            return text
        
        # Сначала пробуем заменить целые слова
        words = text.split()
        converted_words = []
        
        for word in words:
            word_lower = word.lower()
            # Убираем пунктуацию для поиска
            clean_word = re.sub(r'[^\w]', '', word_lower)
            
            if clean_word in cls.WORD_MAP:
                # Сохраняем пунктуацию
                punctuation = re.findall(r'[^\w]', word)
                converted = cls.WORD_MAP[clean_word]
                if punctuation:
                    converted += ''.join(punctuation)
                converted_words.append(converted)
            else:
                converted_words.append(word)
        
        return ' '.join(converted_words)
