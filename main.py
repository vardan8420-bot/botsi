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
from bot.services.analytics import AnalyticsService
from bot.services.code_generator import CodeGenerator
from bot.services.github_manager import GitHubManager

# New Services
from bot.services.web_search import WebSearchService
from bot.services.memory import MemoryService
from bot.services.image_generation import ImageGenerationService
from bot.services.social_media_real import SocialMediaManager as RealSocialMediaManager
from bot.services.smm_marketing import SMMMarketingService
from bot.services.mind_sync import MindSyncService
from bot.services.project_architect import ProjectArchitectService
from bot.services.site_auditor import SiteAuditorService
from bot.services.youtube_analyst import YouTubeAnalystService
from bot.services.report_generator import ReportGeneratorService

# Handlers
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
    social_status_command,
    generate_video_command
)
from bot.handlers.analytics_commands import (
    analytics_command,
    activity_command,
    top_users_command,
    model_stats_command,
    cache_stats_command,
    export_data_command,
    language_stats_command
)
from bot.handlers.code_commands import (
    generate_code_command,
    analyze_code_command,
    fix_code_command,
    explain_code_command,
    refactor_code_command,
    generate_tests_command,
    github_status_command
)
from bot.handlers.github_commands import (
    github_repos_command,
    github_create_repo_command,
    github_create_file_command,
    github_info_command
)
from bot.handlers.messages import (
    handle_text_message,
    handle_voice_message
)

# New Handlers
from bot.handlers.advanced_commands import (
    search_command,
    remember_command,
    recall_command,
    forget_command,
    image_command
)
from bot.handlers.smm_commands import (
    smm_plan_command,
    target_audience_command,
    sales_funnel_command,
    copywriting_command,
    hashtags_command,
    competitor_command
)
from bot.handlers.web_commands import create_site_command, audit_site_command
from bot.handlers.business_commands import youtube_analyze_command, excel_report_command
from bot.handlers.social_scheduler import (
    schedule_instagram_command,
    autopost_status_command,
    cancel_post_command,
    scheduled_posts_worker,
    list_posts_command,
    post_now_command,
)
from bot.handlers.social_commands import (
    post_instagram_command,
    post_facebook_command,
    social_status_real_command
)
from bot.handlers.autonomy_commands import (
    autonomy_on_command,
    autonomy_off_command,
    autonomy_status_command,
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
    # Запускаем фоновый воркер автопостинга
    try:
        application.job_queue.run_repeating(scheduled_posts_worker, interval=60, first=10)
        print("✅ Автопостинг воркер запущен (каждую минуту)")
    except Exception as e:
        print(f"⚠️ Не удалось запустить воркер автопостинга: {e}")


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
    
    # Инициализация сервисов (Этапы 2-4)
    content_generator = ContentGenerator(Config.OPENAI_API_KEY)
    analytics = AnalyticsService(db)
    ai_code_generator = CodeGenerator(Config.OPENAI_API_KEY)
    github_manager = GitHubManager(Config.GITHUB_TOKEN)
    
    # Инициализация НОВЫХ сервисов (Этап 5+)
    web_search = WebSearchService(Config.TAVILY_API_KEY)
    memory = MemoryService(Config.OPENAI_API_KEY)
    image_gen = ImageGenerationService(Config.OPENAI_API_KEY)
    
    social_media_real = RealSocialMediaManager(
        instagram_username=Config.INSTAGRAM_USERNAME,
        instagram_password=Config.INSTAGRAM_PASSWORD,
        facebook_token=Config.FACEBOOK_ACCESS_TOKEN
    )
    
    smm_marketing = SMMMarketingService(ai.client)
    mind_sync = MindSyncService(ai.client, memory)
    project_architect = ProjectArchitectService(ai.client, github_manager)
    site_auditor = SiteAuditorService(ai.client)
    youtube_analyst = YouTubeAnalystService(ai.client)
    report_generator = ReportGeneratorService()
    
    # Создание приложения
    application = ApplicationBuilder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Сохраняем зависимости в bot_data
    application.bot_data['db'] = db
    application.bot_data['ai'] = ai
    application.bot_data['config'] = Config
    application.bot_data['content_generator'] = content_generator
    application.bot_data['analytics'] = analytics
    application.bot_data['code_generator'] = ai_code_generator
    application.bot_data['github_manager'] = github_manager
    
    # Новые сервисы
    application.bot_data['web_search'] = web_search
    application.bot_data['memory'] = memory
    application.bot_data['image_generation'] = image_gen
    application.bot_data['social_media_real'] = social_media_real
    application.bot_data['smm_marketing'] = smm_marketing
    application.bot_data['mind_sync'] = mind_sync
    application.bot_data['project_architect'] = project_architect
    application.bot_data['site_auditor'] = site_auditor
    application.bot_data['youtube_analyst'] = youtube_analyst
    application.bot_data['report_generator'] = report_generator
    
    # --- Регистрация обработчиков команд ---
    
    # Базовые
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", help_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Контент
    application.add_handler(CommandHandler("generate_blog", generate_blog_command))
    application.add_handler(CommandHandler("generate_post", generate_post_command))
    application.add_handler(CommandHandler("generate_script", generate_script_command))
    application.add_handler(CommandHandler("generate_ad", generate_ad_command))
    application.add_handler(CommandHandler("generate_video", generate_video_command))
    
    # Аналитика
    application.add_handler(CommandHandler("analytics", analytics_command))
    application.add_handler(CommandHandler("activity", activity_command))
    application.add_handler(CommandHandler("top_users", top_users_command))
    application.add_handler(CommandHandler("model_stats", model_stats_command))
    application.add_handler(CommandHandler("cache_stats", cache_stats_command))
    application.add_handler(CommandHandler("export_data", export_data_command))
    application.add_handler(CommandHandler("language_stats", language_stats_command))
    
    # Код & GitHub (старый и новый)
    application.add_handler(CommandHandler("generate_code", generate_code_command))
    application.add_handler(CommandHandler("analyze_code", analyze_code_command))
    application.add_handler(CommandHandler("fix_code", fix_code_command))
    application.add_handler(CommandHandler("explain_code", explain_code_command))
    application.add_handler(CommandHandler("refactor_code", refactor_code_command))
    application.add_handler(CommandHandler("generate_tests", generate_tests_command))
    application.add_handler(CommandHandler("github_status", github_status_command))
    
    # GitHub (Advanced)
    application.add_handler(CommandHandler("github_repos", github_repos_command))
    application.add_handler(CommandHandler("github_create_repo", github_create_repo_command))
    application.add_handler(CommandHandler("github_create_file", github_create_file_command))
    application.add_handler(CommandHandler("github_info", github_info_command))
    
    # Поиск & Память & Изображения
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("remember", remember_command))
    application.add_handler(CommandHandler("recall", recall_command))
    application.add_handler(CommandHandler("forget", forget_command))
    application.add_handler(CommandHandler("image", image_command))
    
    # Соцсети (Real)
    application.add_handler(CommandHandler("post_instagram", post_instagram_command))
    application.add_handler(CommandHandler("post_facebook", post_facebook_command))
    application.add_handler(CommandHandler("social_status", social_status_real_command))
    # Автопостинг
    application.add_handler(CommandHandler("schedule_instagram", schedule_instagram_command))
    application.add_handler(CommandHandler("autopost_status", autopost_status_command))
    application.add_handler(CommandHandler("cancel_post", cancel_post_command))
    application.add_handler(CommandHandler("list_posts", list_posts_command))
    application.add_handler(CommandHandler("post_now", post_now_command))
    # Автономия
    application.add_handler(CommandHandler("autonomy_on", autonomy_on_command))
    application.add_handler(CommandHandler("autonomy_off", autonomy_off_command))
    application.add_handler(CommandHandler("autonomy_status", autonomy_status_command))
    
    # SMM & Маркетинг
    application.add_handler(CommandHandler("smm_plan", smm_plan_command))
    application.add_handler(CommandHandler("target_audience", target_audience_command))
    application.add_handler(CommandHandler("sales_funnel", sales_funnel_command))
    application.add_handler(CommandHandler("copywriting", copywriting_command))
    application.add_handler(CommandHandler("hashtags", hashtags_command))
    application.add_handler(CommandHandler("competitor", competitor_command))
    
    # Web Architect
    application.add_handler(CommandHandler("create_site", create_site_command))
    application.add_handler(CommandHandler("audit_site", audit_site_command))
    
    # Business & Analytics
    application.add_handler(CommandHandler("youtube", youtube_analyze_command))
    application.add_handler(CommandHandler("report_excel", excel_report_command))
    
    # Обработчики сообщений
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
