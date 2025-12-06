"""
Botsi - AI Super Bot
Главный файл бота
"""
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.error import Conflict
import os
import sys
import asyncio
import time
from datetime import datetime
from typing import Dict, Optional

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from modules.ai_handler import AIHandler
from modules.armenian_nlp import ArmenianNLP
from modules.translit_converter import TranslitConverter
from modules.cache_manager import CacheManager


# Инициализация конфигурации
config = Config()

if not config.BOT_TOKEN:
    print("❌ Ошибка: BOT_TOKEN не найден в переменных окружения!")
    exit(1)

# Инициализация модулей
ai_handler = AIHandler(config)
nlp = ArmenianNLP()
translit_converter = TranslitConverter()
cache_manager = CacheManager(default_ttl=config.CACHE_TTL)

# Хранилище контекста пользователей
user_contexts: Dict[int, Dict] = {}


def load_system_prompt(language: str = 'hy') -> str:
    """
    Загрузка системного промпта
    
    Args:
        language: Язык промпта ('hy', 'ru', 'en')
        
    Returns:
        Системный промпт
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(
            current_dir,
            'data',
            'prompts',
            f'system_prompt_{language}.txt'
        )
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"⚠️ Ошибка загрузки промпта: {e}")
        # Возвращаем базовый промпт
        if language == 'hy':
            return "Դու Botsi ես - խելացի AI օգնականը։ Պատասխանիր հայերեն։"
        elif language == 'ru':
            return "Ты Botsi - умный AI помощник. Отвечай на русском."
        else:
            return "You are Botsi - a smart AI assistant. Respond in English."

async def cleanup_webhook(app):
    """
    Очистка webhook перед запуском
    
    Args:
        app: Приложение бота
    """
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook очищен, pending updates удалены")
    except Exception as e:
        print(f"⚠️ Не удалось очистить webhook: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка обычных сообщений (без обязательного /start)
    
    Args:
        update: Обновление от Telegram
        context: Контекст бота
    """
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Автоматическая инициализация пользователя
    if user_id not in user_contexts:
        user_contexts[user_id] = {
            'history': [],
            'language': 'hy',  # По умолчанию армянский
            'started_at': datetime.now(),
            'message_count': 0
        }
        print(f"✅ Новый пользователь инициализирован: {user_id}")
    
    user_context = user_contexts[user_id]
    user_context['message_count'] = user_context.get('message_count', 0) + 1
    
    # Определение языка
    detected_lang = nlp.detect_language(user_message)
    
    # Если это транслит, конвертируем в армянский
    if detected_lang == 'hy-translit':
        armenian_text = translit_converter.convert_to_armenian(user_message)
        if armenian_text != user_message:
            user_message = armenian_text
            detected_lang = 'hy'
            # Отправляем конвертированный текст пользователю
            await update.message.reply_text(
                f"📝 Конвертировано: {armenian_text}",
                quote=False
            )
    
    # Обновление языка пользователя
    if detected_lang in ['hy', 'ru', 'en']:
        user_context['language'] = detected_lang
    
    language = user_context['language']
    
    # Проверка кеша
    cached_response = None
    if config.CACHE_ENABLED:
        cached_response = cache_manager.get(user_message)
    
    if cached_response:
        print(f"💾 Ответ из кеша для пользователя {user_id}")
        await update.message.reply_text(cached_response)
        # Обновляем историю
        user_context['history'].append({
            'user': user_message,
            'bot': cached_response,
            'timestamp': datetime.now()
        })
        # Ограничиваем историю до 10 сообщений
        if len(user_context['history']) > 10:
            user_context['history'] = user_context['history'][-10:]
        return
    
    # Загрузка системного промпта
    system_prompt = load_system_prompt(language)
    
    # Получение ответа от AI
    response = await ai_handler.get_response(
        user_message=user_message,
        user_context=user_context,
        language=language,
        system_prompt=system_prompt
    )
    
    if not response:
        # Fallback ответ
        if language == 'hy':
            response = "Ներողություն, չկարողացա պատասխանել։ Կարող եք կրկին փորձել։"
        elif language == 'ru':
            response = "Извините, не смог ответить. Попробуйте еще раз."
        else:
            response = "Sorry, couldn't respond. Please try again."
    
    # Сохранение в кеш
    if config.CACHE_ENABLED:
        cache_manager.set(user_message, response)
    
    # Отправка ответа
    await update.message.reply_text(response)
    
    # Обновление истории
    user_context['history'].append({
        'user': user_message,
        'bot': response,
        'timestamp': datetime.now()
    })
    
    # Ограничиваем историю до 10 сообщений
    if len(user_context['history']) > 10:
        user_context['history'] = user_context['history'][-10:]
    
    # Очистка просроченного кеша (периодически)
    if user_context['message_count'] % 10 == 0:
        cleared = cache_manager.clear_expired()
        if cleared > 0:
            print(f"🧹 Очищено {cleared} просроченных записей из кеша")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /help
    
    Args:
        update: Обновление от Telegram
        context: Контекст бота
    """
    user_id = update.effective_user.id
    language = user_contexts.get(user_id, {}).get('language', 'hy')
    
    if language == 'hy':
        help_text = """🤖 Botsi - AI օգնական

📋 Հասանելի հրամաններ:
/help - Ցուցադրել այս հաղորդագրությունը
/language - Փոխել լեզուն (hy|ru|en)
/stats - Ցուցադրել վիճակագրությունը
/reset - Մաքրել զրույցի պատմությունը

💡 Պարզապես գրեք ինձ - /start-ի կարիք չկա!
"""
    elif language == 'ru':
        help_text = """🤖 Botsi - AI помощник

📋 Доступные команды:
/help - Показать это сообщение
/language - Сменить язык (hy|ru|en)
/stats - Показать статистику
/reset - Очистить историю разговора

💡 Просто напишите мне - /start не нужен!
"""
    else:
        help_text = """🤖 Botsi - AI Assistant

📋 Available commands:
/help - Show this message
/language - Change language (hy|ru|en)
/stats - Show statistics
/reset - Clear conversation history

💡 Just write to me - no /start needed!
"""
    
    await update.message.reply_text(help_text)


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /language
    
    Args:
        update: Обновление от Telegram
        context: Контекст бота
    """
    user_id = update.effective_user.id
    
    # Инициализация если нужно
    if user_id not in user_contexts:
        user_contexts[user_id] = {
            'history': [],
            'language': 'hy',
            'started_at': datetime.now(),
            'message_count': 0
        }
    
    if context.args and len(context.args) > 0:
        lang = context.args[0].lower()
        if lang in ['hy', 'ru', 'en']:
            user_contexts[user_id]['language'] = lang
            
            if lang == 'hy':
                await update.message.reply_text("✅ Լեզուն փոխվեց հայերեն")
            elif lang == 'ru':
                await update.message.reply_text("✅ Язык изменен на русский")
            else:
                await update.message.reply_text("✅ Language changed to English")
        else:
            await update.message.reply_text(
                "❌ Неверный язык. Используйте: /language hy|ru|en"
            )
    else:
        current_lang = user_contexts[user_id].get('language', 'hy')
        await update.message.reply_text(
            f"🌐 Текущий язык: {current_lang}\n"
            f"Используйте: /language hy|ru|en"
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /stats
    
    Args:
        update: Обновление от Telegram
        context: Контекст бота
    """
    user_id = update.effective_user.id
    
    if user_id not in user_contexts:
        await update.message.reply_text("📊 Статистика недоступна")
        return
    
    user_context = user_contexts[user_id]
    language = user_context.get('language', 'hy')
    
    message_count = user_context.get('message_count', 0)
    history_size = len(user_context.get('history', []))
    started_at = user_context.get('started_at', datetime.now())
    
    if language == 'hy':
        stats_text = f"""📊 Ձեր վիճակագրությունը:

💬 Հաղորդագրություններ: {message_count}
📝 Պատմության չափ: {history_size}
🌐 Լեզու: {language}
🕐 Սկսվել է: {started_at.strftime('%Y-%m-%d %H:%M')}
"""
    elif language == 'ru':
        stats_text = f"""📊 Ваша статистика:

💬 Сообщений: {message_count}
📝 Размер истории: {history_size}
🌐 Язык: {language}
🕐 Начато: {started_at.strftime('%Y-%m-%d %H:%M')}
"""
    else:
        stats_text = f"""📊 Your statistics:

💬 Messages: {message_count}
📝 History size: {history_size}
🌐 Language: {language}
🕐 Started: {started_at.strftime('%Y-%m-%d %H:%M')}
"""
    
    await update.message.reply_text(stats_text)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /reset
    
    Args:
        update: Обновление от Telegram
        context: Контекст бота
    """
    user_id = update.effective_user.id
    
    if user_id in user_contexts:
        user_contexts[user_id]['history'] = []
        
        language = user_contexts[user_id].get('language', 'hy')
        
        if language == 'hy':
            await update.message.reply_text("✅ Պատմությունը մաքրվեց")
        elif language == 'ru':
            await update.message.reply_text("✅ История очищена")
        else:
            await update.message.reply_text("✅ History cleared")
    else:
        await update.message.reply_text("ℹ️ История уже пуста")


def main():
    """Главная функция запуска бота"""
    print("🚀 Запуск Botsi...")
    
    # Создание приложения
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reset", reset_command))
    
    # Регистрация обработчика сообщений (БЕЗ обязательного /start)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    # Очистка webhook и запуск polling
    print("🧹 Очистка webhook...")
    try:
        # Используем asyncio.run для очистки webhook перед запуском
        asyncio.run(cleanup_webhook(app))
    except Exception as e:
        print(f"⚠️ Ошибка при очистке: {e}")
    
    # Запуск polling - он создаст свой event loop
    print("⏳ Запуск polling...")
    try:
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    except Conflict as e:
        print(f"⚠️ Конфликт: {e}")
        print("💡 Остановите другие сервисы с этим ботом в Railway")
        import sys
        sys.exit(0)
    except KeyboardInterrupt:
        print("⏹️ Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main()

