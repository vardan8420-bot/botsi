"""
Команды для расширенных функций (поиск, память, изображения)
"""
from telegram import Update
from telegram.ext import ContextTypes


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /search - поиск в интернете"""
    web_search = context.bot_data.get('web_search')
    
    if not web_search or not web_search.is_available:
        await update.message.reply_text(
            "⚠️ Поиск недоступен. Добавьте TAVILY_API_KEY в переменные окружения.\n\n"
            "Получить ключ: https://tavily.com (бесплатно 1000 запросов/месяц)"
        )
        return
    
    if not context.args:
        await update.message.reply_text("💡 Использование: /search <запрос>")
        return
    
    query = ' '.join(context.args)
    await update.message.reply_text(f"🔍 Ищу: {query}...")
    
    result = await web_search.search(query, max_results=3)
    
    if result['success']:
        response = f"🌐 **Результаты поиска:** {query}\n\n"
        
        for i, item in enumerate(result['results'], 1):
            response += f"{i}. **{item['title']}**\n"
            response += f"{item['content'][:200]}...\n"
            response += f"🔗 {item['url']}\n\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def remember_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /remember - запомнить факт"""
    memory = context.bot_data.get('memory')
    
    if not memory or not memory.is_available:
        await update.message.reply_text("⚠️ Память недоступна")
        return
    
    if not context.args:
        await update.message.reply_text("💡 Использование: /remember <факт>")
        return
    
    fact = ' '.join(context.args)
    user_id = update.effective_user.id
    
    result = await memory.remember(user_id, fact)
    
    if result['success']:
        await update.message.reply_text(f"✅ {result['message']}")
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def recall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /recall - вспомнить факты"""
    memory = context.bot_data.get('memory')
    
    if not memory or not memory.is_available:
        await update.message.reply_text("⚠️ Память недоступна")
        return
    
    user_id = update.effective_user.id
    query = ' '.join(context.args) if context.args else None
    
    result = await memory.recall(user_id, query=query)
    
    if result['success']:
        if result['memories']:
            response = "🧠 **Что я помню о тебе:**\n\n"
            for i, mem in enumerate(result['memories'], 1):
                response += f"{i}. {mem['fact']}\n"
                response += f"   _({mem['category']})_\n\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text("🤷 Пока ничего не помню о тебе")
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def forget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /forget - забыть факты"""
    memory = context.bot_data.get('memory')
    
    if not memory or not memory.is_available:
        await update.message.reply_text("⚠️ Память недоступна")
        return
    
    user_id = update.effective_user.id
    
    result = await memory.forget(user_id)
    
    if result['success']:
        await update.message.reply_text(f"✅ {result['message']}")
    else:
        await update.message.reply_text(f"❌ {result['error']}")


async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /image - генерация изображения"""
    image_gen = context.bot_data.get('image_generation')
    
    if not image_gen:
        await update.message.reply_text("⚠️ Генерация изображений недоступна")
        return
    
    if not context.args:
        await update.message.reply_text(
            "💡 Использование:\n"
            "/image <описание> - бесплатно (Stable Diffusion)\n"
            "/image premium <описание> - платно (DALL-E 3, HD качество)"
        )
        return
    
    # Проверяем режим
    use_premium = context.args[0].lower() == 'premium'
    prompt = ' '.join(context.args[1:]) if use_premium else ' '.join(context.args)
    
    if use_premium:
        await update.message.reply_text(f"🎨 Генерирую HD изображение (DALL-E 3)...\n_{prompt}_", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"🎨 Генерирую изображение (Stable Diffusion)...\n_{prompt}_", parse_mode='Markdown')
    
    result = await image_gen.generate(prompt, use_premium=use_premium)
    
    if result['success']:
        if 'url' in result:
            # DALL-E вернул URL
            await update.message.reply_photo(
                photo=result['url'],
                caption=f"✨ {result['model']}\n\n_{result.get('revised_prompt', prompt)}_",
                parse_mode='Markdown'
            )
        elif 'image_bytes' in result:
            # Stable Diffusion вернул байты
            await update.message.reply_photo(
                photo=result['image_bytes'],
                caption=f"✨ {result['model']}\n\n_{prompt}_",
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(f"❌ {result['error']}")
