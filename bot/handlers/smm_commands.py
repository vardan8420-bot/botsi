"""
Команды для SMM и Маркетинга
"""
from telegram import Update
from telegram.ext import ContextTypes


async def smm_plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /smm_plan - контент-план"""
    smm = context.bot_data.get('smm_marketing')
    
    if not smm:
        await update.message.reply_text("⚠️ Сервис SMM недоступен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "💡 Использование: /smm_plan <ниша> [платформа] [дней]\n"
            "Пример: /smm_plan Кофейня Instagram 7"
        )
        return
    
    niche = context.args[0]
    platform = context.args[1] if len(context.args) > 1 else "Instagram"
    days = int(context.args[2]) if len(context.args) > 2 else 7
    
    await update.message.reply_text(f"📅 Генерирую контент-план для {niche} ({platform}, {days} дней)...")
    
    result = await smm.generate_content_plan(niche, platform, days)
    
    if result['success']:
        await update.message.reply_text(result['plan'], parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def target_audience_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /target_audience - анализ ЦА"""
    smm = context.bot_data.get('smm_marketing')
    
    if not smm:
        await update.message.reply_text("⚠️ Сервис SMM недоступен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "💡 Использование: /target_audience <продукт/услуга>\n"
            "Пример: /target_audience Онлайн-курсы английского"
        )
        return
    
    product = ' '.join(context.args)
    
    await update.message.reply_text(f"👥 Анализирую целевую аудиторию для: {product}...")
    
    result = await smm.analyze_target_audience(product)
    
    if result['success']:
        await update.message.reply_text(result['analysis'], parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def sales_funnel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /sales_funnel - воронка продаж"""
    smm = context.bot_data.get('smm_marketing')
    
    if not smm:
        await update.message.reply_text("⚠️ Сервис SMM недоступен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "💡 Использование: /sales_funnel <продукт/услуга>\n"
            "Пример: /sales_funnel Премиум автомойка"
        )
        return
    
    product = ' '.join(context.args)
    
    await update.message.reply_text(f"🔻 Создаю воронку продаж для: {product}...")
    
    result = await smm.create_sales_funnel(product)
    
    if result['success']:
        await update.message.reply_text(result['funnel'], parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def copywriting_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /copywriting - продающий текст"""
    smm = context.bot_data.get('smm_marketing')
    
    if not smm:
        await update.message.reply_text("⚠️ Сервис SMM недоступен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "💡 Использование: /copywriting <формат> <продукт>\n"
            "Форматы: post, email, ad, landing\n"
            "Пример: /copywriting post Новая коллекция одежды"
        )
        return
    
    format_type = context.args[0]
    product = ' '.join(context.args[1:])
    
    await update.message.reply_text(f"✍️ Пишу продающий текст ({format_type}) для: {product}...")
    
    result = await smm.generate_selling_copy(product, format_type)
    
    if result['success']:
        await update.message.reply_text(result['copy'], parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def hashtags_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /hashtags - генерация хештегов"""
    smm = context.bot_data.get('smm_marketing')
    
    if not smm:
        await update.message.reply_text("⚠️ Сервис SMM недоступен")
        return
    
    if not context.args:
        await update.message.reply_text(
            "💡 Использование: /hashtags <тема>\n"
            "Пример: /hashtags Фитнес и здоровое питание"
        )
        return
    
    topic = ' '.join(context.args)
    
    await update.message.reply_text(f"🏷️ Подбираю хештеги для: {topic}...")
    
    result = await smm.generate_hashtags(topic)
    
    if result['success']:
        await update.message.reply_text(result['hashtags'], parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def competitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /competitor - анализ конкурента"""
    smm = context.bot_data.get('smm_marketing')
    
    if not smm:
        await update.message.reply_text("⚠️ Сервис SMM недоступен")
        return
    
    # Ожидаем формат: /competitor <конкурент> | <наш продукт>
    args_text = ' '.join(context.args)
    if '|' not in args_text:
        await update.message.reply_text(
            "💡 Использование: /competitor <конкурент> | <ваш продукт>\n"
            "Пример: /competitor Nike | Спортивная обувь ручной работы"
        )
        return
    
    competitor, product = args_text.split('|', 1)
    competitor = competitor.strip()
    product = product.strip()
    
    await update.message.reply_text(f"🕵️ Анализирую конкурента {competitor}...")
    
    result = await smm.analyze_competitor(competitor, product)
    
    if result['success']:
        await update.message.reply_text(result['analysis'], parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {result['error']}")
