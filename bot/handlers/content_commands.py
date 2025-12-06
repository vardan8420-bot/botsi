"""
Обработчики команд для генерации контента (Этап 2)
"""
from telegram import Update
from telegram.ext import ContextTypes


async def generate_blog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /generate_blog <тема>"""
    content_gen = context.bot_data.get('content_generator')
    
    if not content_gen:
        await update.message.reply_text("❌ Генератор контента недоступен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 Использование: /generate_blog <тема>\n"
            "Пример: /generate_blog Искусственный интеллект"
        )
        return
    
    topic = ' '.join(context.args)
    user_id = update.effective_user.id
    db = context.bot_data['db']
    user = db.get_or_create_user(user_id)
    language = user.language
    
    await update.message.reply_text("⏳ Генерирую статью...")
    
    article = await content_gen.generate_blog_post(topic, language)
    
    if article:
        # Отправляем по частям если длинный
        max_length = 4000
        if len(article) > max_length:
            parts = [article[i:i+max_length] for i in range(0, len(article), max_length)]
            for part in parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(article)
    else:
        await update.message.reply_text("❌ Не удалось сгенерировать статью")


async def generate_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /generate_post <платформа> <тема>"""
    content_gen = context.bot_data.get('content_generator')
    
    if not content_gen:
        await update.message.reply_text("❌ Генератор контента недоступен")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "📱 Использование: /generate_post <платформа> <тема>\n"
            "Платформы: instagram, youtube, tiktok, facebook\n"
            "Пример: /generate_post instagram Новый продукт"
        )
        return
    
    platform = context.args[0].lower()
    topic = ' '.join(context.args[1:])
    
    if platform not in ['instagram', 'youtube', 'tiktok', 'facebook']:
        await update.message.reply_text(
            "❌ Неверная платформа. Доступны: instagram, youtube, tiktok, facebook"
        )
        return
    
    user_id = update.effective_user.id
    db = context.bot_data['db']
    user = db.get_or_create_user(user_id)
    language = user.language
    
    await update.message.reply_text(f"⏳ Генерирую пост для {platform}...")
    
    post = await content_gen.generate_social_post(topic, platform, language)
    
    if post:
        response = f"📱 **Пост для {platform.title()}:**\n\n"
        response += post['text']
        if post.get('hashtags'):
            response += f"\n\n{post['hashtags']}"
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось сгенерировать пост")


async def generate_script_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /generate_script <тема>"""
    content_gen = context.bot_data.get('content_generator')
    
    if not content_gen:
        await update.message.reply_text("❌ Генератор контента недоступен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🎬 Использование: /generate_script <тема>\n"
            "Пример: /generate_script Обзор нового продукта"
        )
        return
    
    topic = ' '.join(context.args)
    user_id = update.effective_user.id
    db = context.bot_data['db']
    user = db.get_or_create_user(user_id)
    language = user.language
    
    await update.message.reply_text("⏳ Генерирую сценарий...")
    
    script = await content_gen.generate_video_script(topic, 60, language)
    
    if script:
        await update.message.reply_text(f"🎬 **Сценарий видео:**\n\n{script}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось сгенерировать сценарий")


async def generate_ad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /generate_ad <продукт> | <аудитория>"""
    content_gen = context.bot_data.get('content_generator')
    
    if not content_gen:
        await update.message.reply_text("❌ Генератор контента недоступен")
        return
    
    if not context.args or '|' not in ' '.join(context.args):
        await update.message.reply_text(
            "📢 Использование: /generate_ad <продукт> | <аудитория>\n"
            "Пример: /generate_ad Смартфон | Молодежь 18-25"
        )
        return
    
    full_text = ' '.join(context.args)
    parts = full_text.split('|')
    
    if len(parts) != 2:
        await update.message.reply_text("❌ Используйте формат: продукт | аудитория")
        return
    
    product = parts[0].strip()
    audience = parts[1].strip()
    
    user_id = update.effective_user.id
    db = context.bot_data['db']
    user = db.get_or_create_user(user_id)
    language = user.language
    
    await update.message.reply_text("⏳ Генерирую рекламу...")
    
    ad = await content_gen.generate_ad_copy(product, audience, language)
    
    if ad:
        await update.message.reply_text(f"📢 **Рекламный текст:**\n\n{ad}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось сгенерировать рекламу")


async def social_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /social_status - показать доступные платформы"""
    social_manager = context.bot_data.get('social_manager')
    
    if not social_manager:
        await update.message.reply_text("❌ Менеджер соцсетей недоступен")
        return
    
    available = social_manager.get_available_platforms()
    
    if available:
        platforms_text = '\n'.join([f"✅ {p.title()}" for p in available])
        message = f"📱 **Доступные платформы:**\n\n{platforms_text}"
    else:
        message = (
            "⚠️ **Нет доступных платформ**\n\n"
            "Добавьте API ключи в переменные окружения:\n"
            "- INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD\n"
            "- YOUTUBE_API_KEY\n"
            "- TIKTOK_SESSION_ID\n"
            "- FACEBOOK_ACCESS_TOKEN"
        )
    
    await update.message.reply_text(message, parse_mode='Markdown')
