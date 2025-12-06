"""
Команды для управления социальными сетями
"""
from telegram import Update
from telegram.ext import ContextTypes
import os


async def post_instagram_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /post_instagram - опубликовать в Instagram"""
    social = context.bot_data.get('social_media_real')
    
    if not social or not social.instagram_available:
        await update.message.reply_text(
            "⚠️ Instagram недоступен.\n\n"
            "Добавьте в Railway:\n"
            "INSTAGRAM_USERNAME=ваш_логин\n"
            "INSTAGRAM_PASSWORD=ваш_пароль"
        )
        return
    
    # Проверяем что есть фото
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "💡 Использование:\n"
            "1. Отправь фото\n"
            "2. Ответь на него: /post_instagram <текст поста>"
        )
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите текст поста")
        return
    
    caption = ' '.join(context.args)
    
    # Скачиваем фото
    photo = update.message.reply_to_message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_path = f"temp_instagram_{update.effective_user.id}.jpg"
    await file.download_to_drive(image_path)
    
    await update.message.reply_text("📸 Публикую в Instagram...")
    
    result = await social.post_instagram(caption, image_path)
    
    # Удаляем временный файл
    if os.path.exists(image_path):
        os.remove(image_path)
    
    if result['success']:
        await update.message.reply_text(
            f"✅ Опубликовано в Instagram!\n\n"
            f"🔗 {result['url']}"
        )
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def post_facebook_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /post_facebook - опубликовать в Facebook"""
    social = context.bot_data.get('social_media_real')
    
    if not social or not social.facebook_available:
        await update.message.reply_text(
            "⚠️ Facebook недоступен.\n\n"
            "Добавьте в Railway:\n"
            "FACEBOOK_ACCESS_TOKEN=ваш_токен\n\n"
            "Получить токен: https://developers.facebook.com"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "💡 Использование: /post_facebook <текст поста>"
        )
        return
    
    message = ' '.join(context.args)
    
    await update.message.reply_text("📘 Публикую в Facebook...")
    
    result = await social.post_facebook(message)
    
    if result['success']:
        await update.message.reply_text(
            f"✅ Опубликовано в Facebook!\n\n"
            f"🔗 {result['url']}"
        )
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def social_status_real_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /social_status - статус соцсетей"""
    social = context.bot_data.get('social_media_real')
    
    if not social:
        await update.message.reply_text("⚠️ Менеджер соцсетей недоступен")
        return
    
    status = social.get_status()
    
    response = "📱 **Статус социальных сетей:**\n\n"
    
    response += f"Instagram: {'✅' if status['instagram'] else '❌'}\n"
    response += f"Facebook: {'✅' if status['facebook'] else '❌'}\n\n"
    
    if status['available_platforms']:
        response += f"**Доступно:** {', '.join(status['available_platforms'])}\n\n"
        response += "**Команды:**\n"
        if status['instagram']:
            response += "/post_instagram - опубликовать в Instagram\n"
        if status['facebook']:
            response += "/post_facebook - опубликовать в Facebook\n"
    else:
        response += "⚠️ Нет доступных платформ\n\n"
        response += "Добавьте учетные данные в Railway"
    
    await update.message.reply_text(response, parse_mode='Markdown')
