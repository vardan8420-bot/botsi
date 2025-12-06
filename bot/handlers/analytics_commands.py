"""
Команды аналитики (Этап 3)
"""
from telegram import Update
from telegram.ext import ContextTypes
import json


async def analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /analytics - глобальная статистика (только для админов)"""
    analytics = context.bot_data.get('analytics')
    
    if not analytics:
        await update.message.reply_text("❌ Аналитика недоступна")
        return
    
    # TODO: Добавить проверку на админа
    # Пока доступно всем для тестирования
    
    stats = analytics.get_global_stats()
    
    message = f"""📊 **Глобальная статистика бота**

👥 **Пользователи:**
• Всего: {stats['total_users']}
• Активных: {stats['active_users']}

💬 **Сообщения:**
• Всего: {stats['total_messages']}
• Из кеша: {stats['cached_messages']} ({stats['cache_hit_rate']}%)

🌐 **Языки:**
"""
    
    for lang, count in stats['languages'].items():
        message += f"• {lang}: {count}\n"
    
    message += "\n🤖 **Модели AI:**\n"
    for model, count in stats['models_used'].items():
        message += f"• {model}: {count}\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def activity_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /activity [дни] - активность за период"""
    analytics = context.bot_data.get('analytics')
    
    if not analytics:
        await update.message.reply_text("❌ Аналитика недоступна")
        return
    
    days = 7
    if context.args and len(context.args) > 0:
        try:
            days = int(context.args[0])
            if days < 1 or days > 365:
                days = 7
        except ValueError:
            days = 7
    
    activity = analytics.get_user_activity(days)
    
    message = f"""📈 **Активность за {days} дней**

👤 Новых пользователей: {activity['new_users']}
✅ Активных пользователей: {activity['active_users']}
💬 Сообщений: {activity['messages']}
📊 Среднее сообщений на пользователя: {activity['avg_messages_per_user']}
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def top_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /top_users [количество] - топ активных пользователей"""
    analytics = context.bot_data.get('analytics')
    
    if not analytics:
        await update.message.reply_text("❌ Аналитика недоступна")
        return
    
    limit = 10
    if context.args and len(context.args) > 0:
        try:
            limit = int(context.args[0])
            if limit < 1 or limit > 50:
                limit = 10
        except ValueError:
            limit = 10
    
    top_users = analytics.get_top_users(limit)
    
    message = f"🏆 **Топ {limit} активных пользователей**\n\n"
    
    for i, user in enumerate(top_users, 1):
        username = user['username'] if user['username'] != 'Unknown' else f"User {user['telegram_id']}"
        message += f"{i}. @{username}\n"
        message += f"   💬 {user['message_count']} сообщений | 🌐 {user['language']}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def model_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /model_stats - статистика использования моделей"""
    analytics = context.bot_data.get('analytics')
    
    if not analytics:
        await update.message.reply_text("❌ Аналитика недоступна")
        return
    
    stats = analytics.get_model_usage_stats()
    
    message = f"""🤖 **Статистика моделей AI**

📊 Всего запросов: {stats['total_requests']}

**Использование моделей:**
"""
    
    for model, count in stats['models'].items():
        percentage = stats['percentages'].get(model, 0)
        message += f"• {model}: {count} ({percentage}%)\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def cache_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /cache_stats - статистика кеша"""
    analytics = context.bot_data.get('analytics')
    
    if not analytics:
        await update.message.reply_text("❌ Аналитика недоступна")
        return
    
    stats = analytics.get_cache_efficiency()
    
    message = f"""💾 **Статистика кеша**

📊 Всего сообщений: {stats['total_messages']}
✅ Из кеша: {stats['cached_responses']}
📈 Hit rate: {stats['cache_hit_rate']}%

🗄️ Записей в кеше: {stats['cache_entries']}
🎯 Всего попаданий: {stats['total_cache_hits']}
📊 Среднее попаданий на запись: {stats['avg_hits_per_entry']}
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def export_data_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /export_data - экспорт своих данных"""
    analytics = context.bot_data.get('analytics')
    
    if not analytics:
        await update.message.reply_text("❌ Аналитика недоступна")
        return
    
    user_id = update.effective_user.id
    
    await update.message.reply_text("⏳ Экспортирую ваши данные...")
    
    data = analytics.export_user_data(user_id)
    
    if not data:
        await update.message.reply_text("❌ Данные не найдены")
        return
    
    # Сохраняем в JSON файл
    filename = f"user_data_{user_id}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Отправляем файл
    with open(filename, 'rb') as f:
        await update.message.reply_document(
            document=f,
            filename=filename,
            caption=f"📦 Ваши данные экспортированы\n\nВсего сообщений: {data['total_messages']}"
        )
    
    # Удаляем временный файл
    import os
    os.remove(filename)


async def language_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /language_stats - распределение по языкам"""
    analytics = context.bot_data.get('analytics')
    
    if not analytics:
        await update.message.reply_text("❌ Аналитика недоступна")
        return
    
    distribution = analytics.get_language_distribution()
    total = sum(distribution.values())
    
    message = "🌐 **Распределение по языкам**\n\n"
    
    for lang, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = round(count / total * 100, 1) if total > 0 else 0
        lang_names = {
            'hy': '🇦🇲 Армянский',
            'ru': '🇷🇺 Русский',
            'en': '🇬🇧 Английский'
        }
        lang_name = lang_names.get(lang, lang)
        message += f"{lang_name}: {count} ({percentage}%)\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')
