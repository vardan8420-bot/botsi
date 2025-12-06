"""
Команды для управления GitHub проектами
"""
from telegram import Update
from telegram.ext import ContextTypes


async def github_repos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /github_repos - список репозиториев"""
    github = context.bot_data.get('github_manager')
    
    if not github or not github.is_configured():
        await update.message.reply_text("⚠️ GitHub не настроен. Добавьте GITHUB_TOKEN.")
        return
    
    await update.message.reply_text("📦 Загружаю репозитории...")
    
    result = await github.list_repositories(limit=10)
    
    if result['success']:
        response = f"📦 **Ваши репозитории** ({result['count']}):\n\n"
        
        for repo in result['repositories']:
            response += f"**{repo['name']}**\n"
            response += f"{repo['description']}\n"
            response += f"⭐ {repo['stars']} | 🔀 {repo['forks']}\n"
            response += f"🔗 {repo['url']}\n\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def github_create_repo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /github_create_repo - создать репозиторий"""
    github = context.bot_data.get('github_manager')
    
    if not github or not github.is_configured():
        await update.message.reply_text("⚠️ GitHub не настроен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "💡 Использование:\n"
            "/github_create_repo <название> [описание]\n\n"
            "Пример: /github_create_repo my-bot Мой крутой бот"
        )
        return
    
    name = context.args[0]
    description = ' '.join(context.args[1:]) if len(context.args) > 1 else ""
    
    await update.message.reply_text(f"🔨 Создаю репозиторий {name}...")
    
    result = await github.create_repository(name, description)
    
    if result['success']:
        await update.message.reply_text(
            f"✅ Репозиторий создан!\n\n"
            f"📦 {result['name']}\n"
            f"🔗 {result['url']}"
        )
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def github_create_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /github_create_file - создать файл в репозитории"""
    github = context.bot_data.get('github_manager')
    
    if not github or not github.is_configured():
        await update.message.reply_text("⚠️ GitHub не настроен")
        return
    
    # Проверяем что это ответ на сообщение с кодом
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text(
            "💡 Использование:\n"
            "1. Отправь код\n"
            "2. Ответь на него командой:\n"
            "/github_create_file <username/repo> <путь/файл.py> <commit message>"
        )
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ Нужно указать: <repo> <путь> <commit message>"
        )
        return
    
    repo_name = context.args[0]
    file_path = context.args[1]
    commit_message = ' '.join(context.args[2:])
    content = update.message.reply_to_message.text
    
    await update.message.reply_text(f"📝 Создаю файл {file_path}...")
    
    result = await github.create_file(repo_name, file_path, content, commit_message)
    
    if result['success']:
        await update.message.reply_text(
            f"✅ Файл создан!\n\n"
            f"📄 {result['file']}\n"
            f"🔖 Commit: {result['commit']}\n"
            f"🔗 {result['url']}"
        )
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def github_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /github_info - информация о репозитории"""
    github = context.bot_data.get('github_manager')
    
    if not github or not github.is_configured():
        await update.message.reply_text("⚠️ GitHub не настроен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "💡 Использование: /github_info <username/repo>"
        )
        return
    
    repo_name = context.args[0]
    
    await update.message.reply_text(f"📊 Загружаю информацию о {repo_name}...")
    
    result = await github.get_repository_info(repo_name)
    
    if result['success']:
        response = f"📦 **{result['full_name']}**\n\n"
        response += f"{result['description']}\n\n"
        response += f"⭐ Stars: {result['stars']}\n"
        response += f"🔀 Forks: {result['forks']}\n"
        response += f"👀 Watchers: {result['watchers']}\n"
        response += f"💻 Language: {result['language']}\n"
        response += f"📅 Created: {result['created_at']}\n"
        response += f"🔄 Updated: {result['updated_at']}\n\n"
        response += f"🔗 {result['url']}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {result['error']}")
