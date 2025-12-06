"""
Botsi - AI Super Bot
Главный файл приложения
"""
import sys
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.error import Conflict

from config import Config
from database import DatabaseRepository
from bot.ai_handler import AIHandler
from bot.services.content_generator import ContentGenerator
from bot.services.social_media_manager import SocialMediaManager
from bot.handlers.commands import (
    help_command,
    language_command,
    stats_command,
    reset_command
)
from bot.handlers.content_commands import (
    generate_blog_command,
    generate_post_command,
    generate_script_command,
    generate_ad_command,
    social_status_command
)
from bot.handlers.messages import (
    handle_text_message,
    handle_voice_message
)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    print(f"❌ Ошибка: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Произошла ошибка. Попробуйте еще раз."
        )


async def post_init(application):
    """Инициализация после запуска"""
    print("✅ Бот успешно запущен!")
    
    # Удаляем webhook если есть
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook очищен")


def main():
    """Главная функция"""
    print("🚀 Запуск Botsi...")
    
    # Валидация конфигурации
    try:
        Config.validate()
        print("✅ Конфигурация валидна")
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    
    # Инициализация БД
    try:
        db = DatabaseRepository(Config.DATABASE_URL)
        print("✅ База данных подключена")
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        sys.exit(1)
    
    # Инициализация AI
    try:
        ai = AIHandler(
            api_key=Config.OPENAI_API_KEY,
            model_mini=Config.OPENAI_MODEL_MINI,
            model_full=Config.OPENAI_MODEL_FULL,
            gpt4o_probability=Config.GPT4O_PROBABILITY
        )
        print("✅ AI обработчик инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации AI: {e}")
        sys.exit(1)
    
    # Инициализация генератора контента (Этап 2)
    try:
        content_generator = ContentGenerator(Config.OPENAI_API_KEY)
        print("✅ Генератор контента инициализирован")
    except Exception as e:
        print(f"⚠️ Генератор контента недоступен: {e}")
        content_generator = None
    
    # Инициализация менеджера соцсетей (Этап 2)
    try:
        social_manager = SocialMediaManager(Config)
        available_platforms = social_manager.get_available_platforms()
        if available_platforms:
            print(f"✅ Соцсети: {', '.join(available_platforms)}")
        else:
            print("⚠️ Соцсети: нет доступных платформ (добавьте API ключи)")
    except Exception as e:
        print(f"⚠️ Менеджер соцсетей недоступен: {e}")
        social_manager = None
    
    # Создание приложения
    application = ApplicationBuilder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Сохраняем зависимости в bot_data
    application.bot_data['db'] = db
    application.bot_data['ai'] = ai
    application.bot_data['config'] = Config
    application.bot_data['content_generator'] = content_generator
    application.bot_data['social_manager'] = social_manager
    
    # Регистрация обработчиков команд (Этап 1)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", help_command))  # /start = /help
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Регистрация команд генерации контента (Этап 2)
    if content_generator:
        application.add_handler(CommandHandler("generate_blog", generate_blog_command))
        application.add_handler(CommandHandler("generate_post", generate_post_command))
        application.add_handler(CommandHandler("generate_script", generate_script_command))
        application.add_handler(CommandHandler("generate_ad", generate_ad_command))
    
    if social_manager:
        application.add_handler(CommandHandler("social_status", social_status_command))
    
    # Регистрация обработчиков сообщений
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    )
    application.add_handler(
        MessageHandler(filters.VOICE, handle_voice_message)
    )
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Post-init callback
    application.post_init = post_init
    
    # Запуск бота
    print("⏳ Запуск polling...")
    try:
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    except Conflict as e:
        print(f"⚠️ Конфликт: {e}")
        print("💡 Остановите другие экземпляры бота")
        sys.exit(0)
    except KeyboardInterrupt:
        print("⏹️ Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
