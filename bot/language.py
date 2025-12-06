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
        # Базовые
        'barev', 'vonc', 'es', 'inch', 'ka', 'em', 'eq',
        'vor', 'aysor', 'vagh', 'lav', 'shat', 'mer',
        'du', 'yes', 'menq', 'duq', 'nranq',
        # Расширенные
        'xosumes', 'haeren', 'hayeren', 'inchpes', 'uzum',
        'gitem', 'chgitem', 'karox', 'petq', 'uneq',
        'barevdzez', 'shnorhakal', 'mersi', 'xndrem',
        'neroxutyun', 'ctesutyun', 'xosum', 'asum',
        'gnum', 'galis', 'talis', 'berum', 'anum',
        'tesnum', 'lsum', 'grum', 'kardanum',
        'inchu', 'erb', 'qani', 'lezu', 'gisher',
        'aravot', 'cerek', 'mard', 'yerekha', 'txa',
        'geghetsik', 'bayc', 'ete', 'vortev',
        'ayo', 'voch', 'arden', 'miayn'
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
    
    # Популярные слова (расширенный словарь)
    WORD_MAP = {
        # Приветствия и базовые фразы
        'barev': 'բարև',
        'barevdzez': 'բարևձեզ',
        'vonc': 'ո՞նց',
        'inchpes': 'ինչպե՞ս',
        'lav': 'լավ',
        'shnorhakalutyun': 'շնորհակալություն',
        'shnorhakal': 'շնորհակալ',
        'mersi': 'մերսի',
        'xndrem': 'խնդրեմ',
        'neroxutyun': 'ներողություն',
        'nerox': 'ներող',
        'ctesutyun': 'ցտեսություն',
        'hajox': 'հաջող',
        
        # Местоимения
        'es': 'ես',
        'du': 'դու',
        'na': 'նա',
        'menq': 'մենք',
        'duq': 'դուք',
        'nranq': 'նրանք',
        'yes': 'ես',
        'im': 'իմ',
        'qo': 'քո',
        'mer': 'մեր',
        'jer': 'ձեր',
        
        # Глаголы
        'em': 'եմ',
        'es': 'ես',
        'e': 'է',
        'enq': 'ենք',
        'eq': 'եք',
        'en': 'են',
        'uzum': 'ուզում',
        'gitem': 'գիտեմ',
        'chgitem': 'չգիտեմ',
        'karox': 'կարող',
        'karogh': 'կարող',
        'petq': 'պետք',
        'uneq': 'ունե՞ք',
        'unem': 'ունեմ',
        'ka': 'կա',
        'chka': 'չկա',
        'xosumes': 'խոսու՞մես',
        'xosum': 'խոսում',
        'asumes': 'ասու՞մես',
        'asum': 'ասում',
        'gnum': 'գնում',
        'galis': 'գալիս',
        'talis': 'տալիս',
        'tanum': 'տանում',
        'berum': 'բերում',
        'anum': 'անում',
        'linum': 'լինում',
        'tesnum': 'տեսնում',
        'lsum': 'լսում',
        'grum': 'գրում',
        'kardanum': 'կարդանում',
        
        # Вопросительные слова
        'inch': 'ինչ',
        'inchu': 'ինչու',
        'vonc': 'ո՞նց',
        'ur': 'ո՞ւր',
        'erb': 'երբ',
        'qani': 'քանի՞',
        'qanisov': 'քանիսո՞վ',
        'ov': 'ո՞վ',
        'um': 'ո՞ւմ',
        'vori': 'որի՞',
        'voric': 'որի՞ց',
        
        # Существительные
        'haeren': 'հայերեն',
        'hayeren': 'հայերեն',
        'lezu': 'լեզու',
        'or': 'օր',
        'aysor': 'այսօր',
        'vagh': 'վաղ',
        'gisher': 'գիշեր',
        'aravot': 'առավոտ',
        'cerek': 'ցերեկ',
        'erekoyan': 'երեկոյան',
        'jam': 'ժամ',
        'ropе': 'րոպե',
        'taric': 'տարի՞ց',
        'tari': 'տարի',
        'amis': 'ամիս',
        'shabat': 'շաբաթ',
        'mard': 'մարդ',
        'kin': 'կին',
        'txamard': 'տղամարդ',
        'yerekha': 'երեխա',
        'txa': 'տղա',
        'aghchik': 'աղջիկ',
        
        # Прилагательные
        'lav': 'լավ',
        'vat': 'վատ',
        'shat': 'շատ',
        'qich': 'քիչ',
        'mec': 'մեծ',
        'poqr': 'փոքր',
        'nor': 'նոր',
        'hin': 'հին',
        'geghetsik': 'գեղեցիկ',
        'shat': 'շատ',
        'lriv': 'լրիվ',
        
        # Предлоги и союзы
        'u': 'ու',
        'ev': 'և',
        'kam': 'կամ',
        'bayc': 'բայց',
        'vor': 'որ',
        'ete': 'եթե',
        'qani': 'քանի',
        'vortev': 'որտև',
        'inch': 'ինչ',
        'mi': 'մի',
        
        # Числа
        'mek': 'մեկ',
        'erku': 'երկու',
        'ereq': 'երեք',
        'chors': 'չորս',
        'hing': 'հինգ',
        'vec': 'վեց',
        'yot': 'յոթ',
        'ut': 'ութ',
        'inn': 'ինն',
        'tas': 'տաս',
        
        # Частицы
        'che': 'չէ',
        'ayo': 'այո',
        'voch': 'ոչ',
        'mi': 'մի',
        'el': 'էլ',
        'arden': 'արդեն',
        'dzerj': 'դեռ',
        'miayn': 'միայն',
        'het': 'հետ',
        'masin': 'մասին',
        'hamar': 'համար',
        
        # Семья
        'mayr': 'մայր',
        'hayr': 'հայր',
        'eghbayr': 'եղբայր',
        'qoyr': 'քույր',
        'tatevik': 'տատևիկ',
        'papik': 'պապիկ',
        'yntaniq': 'ընտանիք',
        'azgakan': 'ազգական',
        
        # Еда и напитки
        'hac': 'հաց',
        'jur': 'ջուր',
        'kat': 'կաթ',
        'surj': 'սուրճ',
        'tey': 'թեյ',
        'mis': 'միս',
        'banjar': 'բանջար',
        'mrgov': 'մրգով',
        'khorovac': 'խորոված',
        'aghchan': 'աղցան',
        
        # Цвета
        'karmir': 'կարմիր',
        'kapuyt': 'կապույտ',
        'kanach': 'կանաչ',
        'deghinn': 'դեղին',
        'sev': 'սև',
        'spitak': 'սպիտակ',
        'gris': 'գրիս',
        'khnguyn': 'խնգույն',
        
        # Места
        'tun': 'տուն',
        'ashkhatanq': 'աշխատանք',
        'dprocakan': 'դպրոցական',
        'dprocq': 'դպրոց',
        'hamalsaran': 'համալսարան',
        'poghoc': 'փողոց',
        'qaghaqa': 'քաղաքա',
        'qaghaqi': 'քաղաքի',
        'gyugh': 'գյուղ',
        'erkir': 'երկիր',
        'hayastan': 'հայաստան',
        'yerevan': 'երևան',
        
        # Действия и состояния
        'sirum': 'սիրում',
        'sirumem': 'սիրումեմ',
        'utelis': 'ուտելիս',
        'utel': 'ուտել',
        'xmel': 'խմել',
        'qnel': 'քնել',
        'artnanal': 'արթնանալ',
        'ashkhatel': 'աշխատել',
        'usanel': 'ուսանել',
        'dasavandel': 'դասավանդել',
        'khosel': 'խոսել',
        'patmel': 'պատմել',
        'harcel': 'հարցնել',
        'pataskhanel': 'պատասխանել',
        
        # Эмоции и чувства
        'urakh': 'ուրախ',
        'tkhur': 'տխուր',
        'barkacut': 'բարկացած',
        'zayracac': 'զայրացած',
        'hognatac': 'հոգնած',
        'zvaracac': 'զվարճացած',
        'shat': 'շատ',
        'qich': 'քիչ',
        
        # Время
        'hima': 'հիմա',
        'ayzhm': 'այժմ',
        'yereko': 'երեկո',
        'vagh': 'վաղ',
        'aysor': 'այսօր',
        'yereg': 'երեկ',
        'vagh': 'վաղը',
        'hetevyal': 'հետևյալ',
        'antsyal': 'անցյալ',
        'ayspisi': 'այսպիսի',
        
        # Погода
        'eghanak': 'եղանակ',
        'areg': 'արեգ',
        'andzrev': 'անձրև',
        'dzuyn': 'ձյուն',
        'qami': 'քամի',
        'tak': 'տակ',
        'tsurt': 'ցուրտ',
        'tak': 'տաք',
        
        # Транспорт
        'meqena': 'մեքենա',
        'avtobus': 'ավտոբուս',
        'metro': 'մետրո',
        'taksi': 'տաքսի',
        'inqnathip': 'ինքնաթիռ',
        'gnacq': 'գնացք',
        
        # Технологии
        'herakhos': 'հեռախոս',
        'kompyuter': 'համակարգիչ',
        'internet': 'ինտերնետ',
        'email': 'էլփոստ',
        'kayan': 'կայան',
        
        # Общие глаголы
        'kara': 'կարա',
        'karogh': 'կարող',
        'piti': 'պիտի',
        'petqa': 'պետքա',
        'chpiti': 'չպիտի',
        'chka': 'չկա',
        'ka': 'կա',
        'unem': 'ունեմ',
        'chunem': 'չունեմ',
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
