"""
Команды для веб-разработки (Project Architect)
"""
from telegram import Update
from telegram.ext import ContextTypes


async def create_site_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /create_site - создать сайт под ключ"""
    architect = context.bot_data.get('project_architect')
    
    if not architect:
        await update.message.reply_text("⚠️ Модуль Архитектора не инициализирован")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🏗️ **Создание сайта под ключ**\n\n"
            "Использование: `/create_site <тема и пожелания>`\n\n"
            "Пример:\n"
            "`/create_site Лендинг для пиццерии, темная тема, неоновые цвета`"
        , parse_mode='Markdown')
        return
    
    topic = ' '.join(context.args)
    
    await update.message.reply_text(
        f"👷‍♂️ **Принято! Я начинаю строительство сайта: {topic}**\n\n"
        "1. 📐 Проектирую структуру...\n"
        "2. 🧱 Генерирую код (HTML/CSS/JS)...\n"
        "3. 🚀 Публикую на GitHub...\n\n"
        "⏳ *Это займет около 30-60 секунд. Ожидайте...*"
    , parse_mode='Markdown')
    
    # Запуск процесса
    result = await architect.build_and_deploy_site(topic, topic)
    
    if result['success']:
        files_list = "\n".join([f"- `{f}`" for f in result['files']])
        
        await update.message.reply_text(
            f"✅ **САЙТ ГОТОВ!**\n\n"
            f"📁 **Репозиторий:**\n{result['repo_url']}\n\n"
            f"📄 **Созданные файлы:**\n{files_list}\n\n"
            f"🌐 **Ссылка (если подключен Vercel):**\n{result['deploy_url']}\n\n"
            "💡 *Совет: Подключи этот репозиторий в Vercel, и сайт будет онлайн!*"
        , parse_mode='Markdown', disable_web_page_preview=True)
    else:
        await update.message.reply_text(f"❌ Ошибка строительства: {result['error']}")


async def audit_site_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /audit_site - проверить сайт на ошибки"""
    auditor = context.bot_data.get('site_auditor')
    
    if not auditor:
        await update.message.reply_text("⚠️ Модуль Аудитора не инициализирован")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🕵️‍♂️ **QA Аудит сайта**\n\n"
            "Использование: `/audit_site <url>`\n\n"
            "Пример:\n/audit_site https://example.com"
        , parse_mode='Markdown')
        return
    
    url = context.args[0]
    if not url.startswith('http'):
        url = 'https://' + url
        
    await update.message.reply_text(f"🕵️‍♂️ Сканирую сайт {url}... Ищу баги...")
    
    result = await auditor.audit_page(url)
    
    if result['success']:
        await update.message.reply_text(
            f"📋 **ОТЧЕТ ПО АУДИТУ:**\n\n"
            f"{result['report']}"
        , parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ Ошибка аудита: {result['error']}")
