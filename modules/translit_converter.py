"""
Конвертер транслита в армянский
Конвертирует latinov → հայերեն
"""
import json
import os
import re
from typing import Dict


class TranslitConverter:
    """Конвертер транслита в армянский"""
    
    def __init__(self):
        """Инициализация конвертера"""
        self.translit_map = self._load_translit_map()
    
    def _load_translit_map(self) -> Dict:
        """
        Загрузка карты транслитерации
        
        Returns:
            Словарь с картой транслитерации
        """
        try:
            # Путь к файлу с картой транслитерации
            current_dir = os.path.dirname(os.path.abspath(__file__))
            map_path = os.path.join(current_dir, '..', 'data', 'translit_map.json')
            
            with open(map_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'words': data.get('words', {}),
                    'letters': data.get('letters', {})
                }
        except Exception as e:
            print(f"Ошибка загрузки карты транслитерации: {e}")
            return {'words': {}, 'letters': {}}
    
    def convert_to_armenian(self, text: str) -> str:
        """
        Конвертирует транслит в армянский
        
        Примеры:
        voghchuyn → ողջույն
        barev → բարև
        shat lav → շատ լավ
        inchpes es → ինչպես ես
        
        Args:
            text: Текст на транслите
            
        Returns:
            Текст на армянском
        """
        if not text:
            return text
        
        text_lower = text.lower()
        result = text
        
        # Сначала заменяем целые слова
        words_map = self.translit_map.get('words', {})
        for translit_word, armenian_word in words_map.items():
            # Заменяем слово целиком (с границами слов)
            pattern = r'\b' + re.escape(translit_word) + r'\b'
            result = re.sub(pattern, armenian_word, result, flags=re.IGNORECASE)
        
        # Затем заменяем буквы (для слов, которых нет в словаре)
        letters_map = self.translit_map.get('letters', {})
        
        # Сортируем по длине (сначала длинные комбинации: kh, sh, ch, gh, ts)
        sorted_letters = sorted(letters_map.items(), key=lambda x: len(x[0]), reverse=True)
        
        for translit_letter, armenian_letter in sorted_letters:
            result = result.replace(translit_letter, armenian_letter)
            result = result.replace(translit_letter.capitalize(), armenian_letter)
            result = result.replace(translit_letter.upper(), armenian_letter)
        
        return result
    
    def convert_word(self, word: str) -> str:
        """
        Конвертирует одно слово
        
        Args:
            word: Слово на транслите
            
        Returns:
            Слово на армянском
        """
        return self.convert_to_armenian(word)
    
    def is_translit_word(self, word: str) -> bool:
        """
        Проверяет является ли слово транслитом
        
        Args:
            word: Слово для проверки
            
        Returns:
            True если это транслит
        """
        words_map = self.translit_map.get('words', {})
        word_lower = word.lower()
        
        # Проверка на наличие в словаре
        if word_lower in words_map:
            return True
        
        # Проверка на наличие армянских букв
        if re.search(r'[\u0530-\u058F]', word):
            return False
        
        # Если слово состоит из латинских букв и есть в словаре транслита
        if re.match(r'^[a-z]+$', word_lower):
            return True
        
        return False

