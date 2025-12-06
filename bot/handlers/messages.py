"""
Обработчики сообщений
"""
import os
from telegram import Update
from telegram.ext import ContextTypes

from bot.language import LanguageDetector, TranslitConverter


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    db = context.bot_data['db']
    ai = context.bot_data['ai']
    config = context.bot_data['config']
    
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Получаем или создаем пользователя
    user = db.get_or_create_user(
        telegram_id=user_id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )
    
    # Увеличиваем счетчик сообщений
    db.increment_message_count(user_id)
    
    # Определяем язык
    detected_lang = LanguageDetector.detect(user_message)
    
    # Конвертируем транслит если нужно
    original_message = user_message
    if detected_lang == 'hy-translit':
        converted = TranslitConverter.convert(user_message)
        if converted != user_message:
            user_message = converted
            detected_lang = 'hy'
            # Показываем конвертированный текст
            await update.message.reply_text(
                f"📝 {converted}",
                quote=False
            )
    
    # Обновляем язык пользователя
    if detected_lang in ['hy', 'ru', 'en']:
        db.update_user_language(user_id, detected_lang)
        language = detected_lang
    else:
        language = user.language
    
    # Проверяем кеш
    cached_response = None
    if config.CACHE_ENABLED:
        cached_response = db.get_cached_response(user_message)
    
    if cached_response:
        print(f"💾 Ответ из кеша для пользователя {user_id}")
        await update.message.reply_text(cached_response)
        
        # Сохраняем в историю
        db.save_message(
            telegram_id=user_id,
            user_message=original_message,
            bot_response=cached_response,
            language=language,
            model_used='cache',
            is_cached=True
        )
        return
    
    # Загружаем системный промпт
    system_prompt = load_system_prompt(language)
    
    # Получаем историю
    history = db.get_user_history(user_id, limit=config.MAX_CONTEXT_MESSAGES)
    
    # Получаем ответ от AI
    response, model_used = await ai.get_response(
        user_message=user_message,
        system_prompt=system_prompt,
        history=history,
        language=language
    )
    
    if not response:
        # Fallback ответ
        fallback_messages = {
            'hy': 'Ներողություն, չկարողացա պատասխանել։ Կարող եք կրկին փորձել։',
            'ru': 'Извините, не смог ответить. Попробуйте еще раз.',
            'en': 'Sorry, couldn\'t respond. Please try again.'
        }
        response = fallback_messages.get(language, fallback_messages['en'])
        model_used = 'error'
    
    # Сохраняем в кеш
    if config.CACHE_ENABLED and model_used != 'error':
        db.set_cached_response(user_message, response, ttl=config.CACHE_TTL)
    
    # Отправляем ответ
    await update.message.reply_text(response)
    
    # Сохраняем в историю
    db.save_message(
        telegram_id=user_id,
        user_message=original_message,
        bot_response=response,
        language=language,
        model_used=model_used or 'unknown',
        is_cached=False
    )
    
    # Периодическая очистка кеша
    if user.message_count % 10 == 0:
        cleared = db.clear_expired_cache()
        if cleared > 0:
            print(f"🧹 Очищено {cleared} просроченных записей из кеша")


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений"""
    db = context.bot_data['db']
    ai = context.bot_data['ai']
    config = context.bot_data['config']
    
    user_id = update.effective_user.id
    
    # Получаем пользователя
    user = db.get_or_create_user(
        telegram_id=user_id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )
    
    language = user.language
    
    try:
        # Отправляем статус "печатает"
        await update.message.chat.send_action("typing")
        
        # Скачиваем голосовое сообщение
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        
        # Сохраняем временно
        temp_file = f"temp_voice_{user_id}.ogg"
        await file.download_to_drive(temp_file)
        
        # Транскрибируем
        transcribed_text = await ai.transcribe_audio(temp_file)
        
        # Удаляем временный файл
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if not transcribed_text:
            error_messages = {
                'hy': '❌ Չկարողացա ճանաչել ձայնը։ Փորձեք կրկին։',
                'ru': '❌ Не удалось распознать голос. Попробуйте еще раз.',
                'en': '❌ Could not recognize voice. Please try again.'
            }
            await update.message.reply_text(error_messages.get(language, error_messages['en']))
            return
        
        # Показываем распознанный текст
        await update.message.reply_text(f"🎤 {transcribed_text}")
        
        # Обрабатываем как текстовое сообщение
        # Создаем временный update с текстом
        update.message.text = transcribed_text
        await handle_text_message(update, context)
        
    except Exception as e:
        print(f"❌ Ошибка обработки голоса: {e}")
        error_messages = {
            'hy': '❌ Սխալ ձայնի մշակման ժամանակ։',
            'ru': '❌ Ошибка при обработке голоса.',
            'en': '❌ Error processing voice message.'
        }
        await update.message.reply_text(error_messages.get(language, error_messages['en']))


def load_system_prompt(language: str = 'hy') -> str:
    """
    Загрузка системного промпта
    
    Args:
        language: Язык промпта ('hy', 'ru', 'en')
        
    Returns:
        Системный промпт
    """
    prompts = {
        'hy': """Դու Botsi ես - խելացի AI օգնականը։

Քո առաքելությունը՝
- Պատասխանել հայերեն լեզվով
- Լինել օգտակար, ընկերական և պրոֆեսիոնալ
- Տրամադրել ճշգրիտ և հստակ տեղեկատվություն
- Օգնել օգտատերերին իրենց խնդիրների լուծման հարցում

Պատասխանիր կարճ և հստակ, եթե հարցը պարզ է։
Եթե հարցը բարդ է, տուր մանրամասն բացատրություն։""",
        
        'ru': """Ты Botsi - умный AI помощник.

Твоя миссия:
- Отвечать на русском языке
- Быть полезным, дружелюбным и профессиональным
- Предоставлять точную и четкую информацию
- Помогать пользователям решать их задачи

Отвечай кратко и ясно, если вопрос простой.
Если вопрос сложный, дай подробное объяснение.""",
        
        'en': """You are Botsi - a smart AI assistant.

Your mission:
- Respond in English
- Be helpful, friendly and professional
- Provide accurate and clear information
- Help users solve their problems

Answer briefly and clearly if the question is simple.
If the question is complex, give a detailed explanation."""
    }
    
    return prompts.get(language, prompts['en'])
