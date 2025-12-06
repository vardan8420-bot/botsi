"""
Обработчики команд бота
"""
from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    db = context.bot_data['db']
    user_id = update.effective_user.id
    
    # Получаем пользователя
    user = db.get_or_create_user(
        telegram_id=user_id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )
    
    language = user.language
    
    help_texts = {
        'hy': """🤖 **Botsi - AI Օգնական**

📋 **Հիմնական հրամաններ:**
/help - Ցուցադրել այս հաղորդագրությունը
/language - Փոխել լեզուն (hy|ru|en)
/stats - Ցուցադրել վիճակագրությունը
/reset - Մաքրել զրույցի պատմությունը

📝 **Բովանդակության ստեղծում:**
/generate_blog <թեմա> - Ստեղծել հոդված
/generate_post <հարթակ> <թեմա> - Ստեղծել սոց․ ցանցի պոստ
/generate_script <թեմա> - Ստեղծել վիդեո սցենար
/generate_ad <ապրանք> | <լսարան> - Ստեղծել գովազդ
/social_status - Հասանելի սոց․ ցանցեր

📊 **Վերլուծություն:**
/analytics - Գլոբալ վիճակագրություն
/activity [օրեր] - Ակտիվություն
/top_users [քանակ] - Ամենաակտիվ օգտատերեր
/model_stats - AI մոդելների վիճակագրություն
/cache_stats - Քեշի վիճակագրություն
/export_data - Արտահանել ձեր տվյալները
/language_stats - Լեզուների բաշխում

💻 **AI Ծրագրավորող:**
/generate_code <լեզու> <նկարագրություն> - Ստեղծել կոդ
/analyze_code - Վերլուծել կոդը
/fix_code <խնդիր> - Ուղղել կոդը
/explain_code - Բացատրել կոդը
/refactor_code - Վերակառուցել կոդը
/generate_tests - Ստեղծել թեստեր
/github_status - GitHub կարգավիճակ

💡 **Պարզապես գրեք ինձ - /start-ի կարիք չկա!**

🎤 Կարող եք նաև ուղարկել ձայնային հաղորդագրություն։
""",
        'ru': """🤖 **Botsi - AI Помощник**

📋 **Основные команды:**
/help - Показать это сообщение
/language - Сменить язык (hy|ru|en)
/stats - Показать статистику
/reset - Очистить историю разговора

📝 **Генерация контента:**
/generate_blog <тема> - Создать статью
/generate_post <платформа> <тема> - Создать пост для соцсети
/generate_script <тема> - Создать сценарий видео
/generate_ad <продукт> | <аудитория> - Создать рекламу
/social_status - Доступные соцсети

📊 **Аналитика:**
/analytics - Глобальная статистика
/activity [дни] - Активность за период
/top_users [количество] - Топ активных пользователей
/model_stats - Статистика AI моделей
/cache_stats - Статистика кеша
/export_data - Экспортировать ваши данные
/language_stats - Распределение по языкам

💻 **AI Разработчик:**
/generate_code <язык> <описание> - Сгенерировать код
/analyze_code - Анализ кода
/fix_code <проблема> - Исправить код
/explain_code - Объяснить код
/refactor_code - Рефакторинг кода
/generate_tests - Сгенерировать тесты
/github_status - Статус GitHub

💡 **Просто напишите мне - /start не нужен!**

🎤 Вы также можете отправить голосовое сообщение.
""",
        'en': """🤖 **Botsi - AI Assistant**

📋 **Main commands:**
/help - Show this message
/language - Change language (hy|ru|en)
/stats - Show statistics
/reset - Clear conversation history

📝 **Content Generation:**
/generate_blog <topic> - Create blog post
/generate_post <platform> <topic> - Create social media post
/generate_script <topic> - Create video script
/generate_ad <product> | <audience> - Create ad copy
/social_status - Available social platforms

📊 **Analytics:**
/analytics - Global statistics
/activity [days] - Activity for period
/top_users [count] - Top active users
/model_stats - AI models statistics
/cache_stats - Cache statistics
/export_data - Export your data
/language_stats - Language distribution

💻 **AI Developer:**
/generate_code <language> <description> - Generate code
/analyze_code - Analyze code
/fix_code <issue> - Fix code
/explain_code - Explain code
/refactor_code - Refactor code
/generate_tests - Generate tests
/github_status - GitHub status

💡 **Just write to me - no /start needed!**

🎤 You can also send a voice message.
"""
    }
    
    help_text = help_texts.get(language, help_texts['en'])
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /language"""
    db = context.bot_data['db']
    user_id = update.effective_user.id
    
    # Получаем пользователя
    user = db.get_or_create_user(
        telegram_id=user_id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )
    
    if context.args and len(context.args) > 0:
        lang = context.args[0].lower()
        if lang in ['hy', 'ru', 'en']:
            db.update_user_language(user_id, lang)
            
            messages = {
                'hy': '✅ Լեզուն փոխվեց հայերեն',
                'ru': '✅ Язык изменен на русский',
                'en': '✅ Language changed to English'
            }
            
            await update.message.reply_text(messages[lang])
        else:
            await update.message.reply_text(
                '❌ Неверный язык. Используйте: /language hy|ru|en'
            )
    else:
        current_lang = user.language
        await update.message.reply_text(
            f'🌐 Текущий язык: {current_lang}\n'
            f'Используйте: /language hy|ru|en'
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats"""
    db = context.bot_data['db']
    user_id = update.effective_user.id
    
    # Получаем пользователя
    user = db.get_or_create_user(
        telegram_id=user_id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )
    
    stats = db.get_user_stats(user_id)
    language = user.language
    
    if not stats:
        await update.message.reply_text('📊 Статистика недоступна')
        return
    
    created_at = stats['created_at'].strftime('%Y-%m-%d %H:%M')
    
    stats_texts = {
        'hy': f"""📊 **Ձեր վիճակագրությունը:**

💬 Հաղորդագրություններ: {stats['message_count']}
📝 Պատմության չափ: {stats['total_messages']}
🌐 Լեզու: {stats['language']}
🕐 Սկսվել է: {created_at}
""",
        'ru': f"""📊 **Ваша статистика:**

💬 Сообщений: {stats['message_count']}
📝 Всего в истории: {stats['total_messages']}
🌐 Язык: {stats['language']}
🕐 Начато: {created_at}
""",
        'en': f"""📊 **Your statistics:**

💬 Messages: {stats['message_count']}
📝 Total in history: {stats['total_messages']}
🌐 Language: {stats['language']}
🕐 Started: {created_at}
"""
    }
    
    stats_text = stats_texts.get(language, stats_texts['en'])
    await update.message.reply_text(stats_text, parse_mode='Markdown')


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /reset"""
    db = context.bot_data['db']
    user_id = update.effective_user.id
    
    # Получаем пользователя
    user = db.get_or_create_user(
        telegram_id=user_id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )
    
    db.clear_user_history(user_id)
    
    language = user.language
    
    messages = {
        'hy': '✅ Պատմությունը մաքրվեց',
        'ru': '✅ История очищена',
        'en': '✅ History cleared'
    }
    
    message = messages.get(language, messages['en'])
    await update.message.reply_text(message)
