"""
Команды для бизнеса и аналитики (YouTube, Excel)
"""
from telegram import Update
from telegram.ext import ContextTypes
import os 


async def youtube_analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /youtube - анализ видео"""
    analyst = context.bot_data.get('youtube_analyst')
    
    if not analyst:
        await update.message.reply_text("⚠️ Сервис аналитики недоступен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🎥 **Анализ YouTube Видео**\n\n"
            "Использование: `/youtube <ссылка>`\n\n"
            "Пример:\n`/youtube https://youtu.be/...`"
        , parse_mode='Markdown')
        return
    
    url = context.args[0]
    
    await update.message.reply_text("🍿 Смотрю видео... (Это может занять секунд 10-20)")
    
    result = await analyst.get_video_summary(url)
    
    if result['success']:
        await update.message.reply_text(
            f"📺 **РЕЗУЛЬТАТ АНАЛИЗА:**\n\n"
            f"{result['summary']}"
        , parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ Ошибка: {result['error']}")


async def excel_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /report_excel - тестовая генерация отчета"""
    reporter = context.bot_data.get('report_generator')
    
    if not reporter:
        await update.message.reply_text("⚠️ Генератор отчетов недоступен")
        return

    # Это просто демо-команда. В реальности этот сервис будет использоваться другими модулями
    # Но для теста сделаем простой отчет
    
    data = [
        {"Товар": "iPhone 15", "Цена": "1000$", "Продажи": "50"},
        {"Товар": "Samsung S24", "Цена": "950$", "Продажи": "45"},
        {"Товар": "Pixel 8", "Цена": "800$", "Продажи": "30"},
    ]
    
    await update.message.reply_text("📊 Генерирую Excel файл...")
    
    file_path = await reporter.create_excel("sales_report", "Sales Data", data)
    
    if file_path and os.path.exists(file_path):
        await update.message.reply_document(
            document=open(file_path, 'rb'),
            caption="Вот ваш отчет! 📈",
            filename="sales_report.xlsx"
        )
        os.remove(file_path) # Чистим за собой
    else:
        await update.message.reply_text("❌ Не удалось создать файл.")
