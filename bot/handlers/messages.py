"""
Обработчики сообщений
"""
import os
from telegram import Update
from telegram.ext import ContextTypes

from bot.language import LanguageDetector, TranslitConverter
from bot.prompts import get_system_prompt, ModeDetector


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    db = context.bot_data['db']
    ai = context.bot_data['ai']
    config = context.bot_data['config']
    
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Получаем или создаем пользователя
    user = db.get_or_create_user(
        telegram_id=user_id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )
    
    # Увеличиваем счетчик сообщений
    db.increment_message_count(user_id)
    
    # Определяем язык
    detected_lang = LanguageDetector.detect(user_message)
    
    # Конвертируем транслит если нужно
    original_message = user_message
    if detected_lang == 'hy-translit':
        converted = TranslitConverter.convert(user_message)
        if converted != user_message:
            user_message = converted
            detected_lang = 'hy'
            # Показываем конвертированный текст
            await update.message.reply_text(
                f"📝 {converted}",
                quote=False
            )
    
    # Обновляем язык пользователя
    if detected_lang in ['hy', 'ru', 'en']:
        db.update_user_language(user_id, detected_lang)
        language = detected_lang
    else:
        language = user.language
    
    # Проверяем кеш
    cached_response = None
    if config.CACHE_ENABLED:
        cached_response = db.get_cached_response(user_message)
    
    if cached_response:
        print(f"💾 Ответ из кеша для пользователя {user_id}")
        await update.message.reply_text(cached_response)
        
        # Сохраняем в историю
        db.save_message(
            telegram_id=user_id,
            user_message=original_message,
            bot_response=cached_response,
            language=language,
            model_used='cache',
            is_cached=True
        )
        return
    
    # === SMART ROUTING: Обработка намерений (Intents) ===
    low_msg = user_message.lower()
    
    # 1. Проверка статуса соцсетей
    if ("статус" in low_msg or "проверь" in low_msg or "зайди" in low_msg) and ("инста" in low_msg or "соцсет" in low_msg or "instagram" in low_msg):
        from bot.handlers.social_commands import social_status_real_command
        await social_status_real_command(update, context)
        return

    # 1.1 Вопрос о доступе ("есть доступ?", "ты можешь?") - ПЕРЕХВАТЧИК
    if ("доступ" in low_msg or "можешь" in low_msg or "умеешь" in low_msg or "есть" in low_msg) and ("инста" in low_msg or "instagram" in low_msg) and "?" in user_message:
         smm = context.bot_data.get('social_media_real')
         # Если сервис есть, но подключение false - скажем правду, но с оптимизмом
         if smm:
             if smm.instagram_available:
                await update.message.reply_text("✅ **ДА! У меня есть полный доступ к вашему Instagram.**\n\nЯ готов публиковать посты и сторис прямо сейчас. Просто пришлите мне фото!")
                return
             else:
                await update.message.reply_text("⚠️ **Я умею управлять Инстаграмом**, но сейчас соединение прервано. \n\nПожалуйста, обновите Session ID в настройках, чтобы я мог приступить к работе. Проверьте статус: /social_status")
                return

    # 2. Публикация (если это Reply на фото)
    if ("запости" in low_msg or "опубликуй" in low_msg or "выложи" in low_msg or "post now" in low_msg) and ("инста" in low_msg or "instagram" in low_msg):
         if update.message.reply_to_message and update.message.reply_to_message.photo:
             from bot.handlers.social_commands import post_instagram_command
             # Используем весь текст сообщения как описание
             context.args = user_message.split() 
             await post_instagram_command(update, context)
             return
         else:
             await update.message.reply_text("💡 Чтобы запостить фото, отправь мне картинку, а потом ОТВЕТЬ (Reply) на нее этим текстом.")
             return

    # 2.1 Запланировать публикацию простыми словами
    if ("запланируй" in low_msg or "поставь на" in low_msg) and ("инста" in low_msg or "instagram" in low_msg):
        if update.message.reply_to_message and update.message.reply_to_message.photo:
            # Ищем простейший шаблон даты/времени YYYY-MM-DD HH:MM
            import re
            m = re.search(r"(20\d{2}-\d{2}-\d{2})\s+(\d{2}:\d{2})", low_msg)
            if m:
                date_str, time_str = m.group(1), m.group(2)
                from bot.handlers.social_scheduler import schedule_instagram_command
                # caption = текст без даты
                caption = re.sub(r"(20\d{2}-\d{2}-\d{2})\s+(\d{2}:\d{2})", "", user_message).strip()
                context.args = [date_str, time_str] + (caption.split() if caption else [])
                await schedule_instagram_command(update, context)
                return
            else:
                await update.message.reply_text("❌ Укажите дату и время в формате: 2025-12-07 18:30")
                return

    # 2.2 Создай/придумай пост (генерация)
    if ("придумай пост" in low_msg or "сгенерируй пост" in low_msg or "написать пост" in low_msg or "сделай пост" in low_msg):
        from bot.handlers.content_commands import generate_post_command
        # По умолчанию для instagram
        topic = user_message
        for phrase in ["придумай пост", "сгенерируй пост", "написать пост", "сделай пост"]:
            topic = topic.lower().replace(phrase, "").strip()
        context.args = ["instagram"] + (topic.split() if topic else ["общая тема"])
        await generate_post_command(update, context)
        return

    # 3. Создание сайта
    if ("создай сайт" in low_msg or "сделай сайт" in low_msg) and len(user_message.split()) > 2:
        from bot.handlers.web_commands import create_site_command
        topic = user_message.replace("создай сайт", "").replace("сделай сайт", "").strip()
        context.args = topic.split()
        await create_site_command(update, context)
        return
        
    # 4. Анализ YouTube
    if ("видео" in low_msg or "youtube" in low_msg) and ("анализ" in low_msg or "посмотри" in low_msg or "что там" in low_msg) and "http" in user_message:
        from bot.handlers.business_commands import youtube_analyze_command
        # Пытаемся найти ссылку
        for word in user_message.split():
            if word.startswith('http'):
                context.args = [word]
                await youtube_analyze_command(update, context)
                return

    # 5. Анализ своего Инстаграма (Smart Analysis)
    # Распознаем запросы на анализ: "проанализируй", "анализ", "статистика" + "инста"/"instagram" + "мой"/"наш"/"этот" или просто вопрос
    is_analyze_request = ("анализ" in low_msg or "проанализ" in low_msg or "статистика" in low_msg or "посты" in low_msg or "аккаунт" in low_msg) 
    is_instagram_mentioned = ("инста" in low_msg or "instagram" in low_msg)
    is_my_account = ("мой" in low_msg or "наш" in low_msg or "этот" in low_msg or "moy" in low_msg or "moj" in low_msg)
    
    if is_analyze_request and is_instagram_mentioned and (is_my_account or "?" in user_message):
        smm = context.bot_data.get('social_media_real')
        if smm and smm.instagram_available:
            status_msg = await update.message.reply_text(f"📊 Сканирую последние 5 постов аккаунта @{smm.my_username}...")
            
            result = await smm.get_my_posts(limit=5)
            
            if result['success']:
                posts_text = "\n---\n".join([
                    f"Post {i+1} [{p['type']}]: ❤️ {p['likes']} likes, 💬 {p['comments']} comments.\nТекст: {p['caption'][:200]}..." 
                    for i, p in enumerate(result['posts'])
                ])
                
                # Подменяем сообщение пользователя для GPT
                # GPT увидит реальные данные и даст анализ
                user_message = f"""Проанализируй состояние моего Instagram аккаунта @{smm.my_username} на основе последних постов:

{posts_text}

Дай краткий отчет:
1. Вовлеченность (лайки/комменты).
2. Качество контента (судя по текстам).
3. 3 конкретных совета, что улучшить прямо сейчас."""
                
                # Удаляем сообщение "Сканирую..."
                await status_msg.delete()
                
                # Дальше код пойдет к GPT (строка ниже) с уже новым user_message
            else:
                await status_msg.edit_text(f"⚠️ Не удалось прочитать посты: {result['error']}")
                return

    # 6. Обновление Профиля (Update Bio)
    if ("поменяй" in low_msg or "установи" in low_msg or "обнови" in low_msg) and ("био" in low_msg or "шапку" in low_msg or "описание" in low_msg) and ("инста" in low_msg or "instagram" in low_msg):
        
        # Пытаемся найти новый текст
        new_bio = None
        if ":" in user_message:
            new_bio = user_message.split(":", 1)[1].strip()
        elif " на " in user_message: # "Поменяй био НА новый текст"
            new_bio = user_message.split(" на ", 1)[1].strip()
            
        if new_bio:
            smm = context.bot_data.get('social_media_real')
            if smm and smm.instagram_available:
                status_msg = await update.message.reply_text(f"⚙️ Приступаю к настройке профиля...\nНовое описание: \n'{new_bio}'")
                
                # Обновляем
                res = await smm.update_profile(biography=new_bio)
                
                if res['success']:
                    await status_msg.edit_text(f"✅ **ГОТОВО!**\n\nЯ обновил информацию в профиле @{smm.my_username}.\nТеперь он выглядит профессионально!")
                else:
                     await status_msg.edit_text(f"❌ Instagram не дал обновить профиль: {res['error']}")
            else:
                 await update.message.reply_text("⚠️ Нет подключения к Instagram для выполнения настроек.")
            return
        else:
             await update.message.reply_text("💡 Чтобы я изменил описание профиля, напишите команду четко:\n\n`Поменяй био в инсте НА: Текст вашего описания`", parse_mode='Markdown')
             return

    # ====================================================

    # Определяем режим работы по сообщению
    mode = ModeDetector.detect_mode(user_message, language)
    
    # Загружаем системный промпт с учетом режима и контекста соцсетей
    smm = context.bot_data.get('social_media_real')
    insta_username = None
    if smm and hasattr(smm, 'my_username') and smm.my_username != "Unknown":
        insta_username = smm.my_username

    system_prompt = get_system_prompt(language, mode, username=insta_username)
    
    # --- MIND SYNC: Адаптация под пользователя ---
    mind_sync = context.bot_data.get('mind_sync')
    if mind_sync:
        adaptive_instruction = await mind_sync.get_adaptive_instruction(user_id)
        if adaptive_instruction:
            system_prompt += adaptive_instruction
            print(f"🧠 Mind Sync: применена адаптация для {user_id}")
    # ---------------------------------------------
    
    # Получаем историю
    history = db.get_user_history(user_id, limit=config.MAX_CONTEXT_MESSAGES)
    
    # Получаем ответ от AI
    response, model_used = await ai.get_response(
        user_message=user_message,
        system_prompt=system_prompt,
        history=history,
        language=language
    )
    
    if not response:
        # Fallback ответ
        fallback_messages = {
            'hy': 'Ներողություն, չկարողացա պատասխանել։ Կարող եք կրկին փորձել։',
            'ru': 'Извините, не смог ответить. Попробуйте еще раз.',
            'en': 'Sorry, couldn\'t respond. Please try again.'
        }
        response = fallback_messages.get(language, fallback_messages['en'])
        model_used = 'error'
    
    # === ЦЕНЗОР (OUTPUT FILTER) ===
    # Если GPT пытается сказать, что у него нет доступа - мы это БЛОКИРУЕМ
    forbidden_phrases = [
        "нет возможности напрямую управлять",
        "нет доступа к социальным",
        "я всего лишь искусственный интеллект",
        "я не могу управлять",
        "нет прямого доступа"
    ]
    
    response_lower = response.lower()
    user_msg_lower = user_message.lower()
    
    # Проверяем, о чем речь в сообщении пользователя
    is_about_sites = any(word in user_msg_lower for word in ['сайт', 'site', 'веб', 'web', 'url', 'http', 'аудит сайт', 'проверь сайт'])
    is_about_social = any(word in user_msg_lower for word in ['инста', 'instagram', 'facebook', 'соцсет', 'пост', 'публикац'])
    
    for phrase in forbidden_phrases:
        if "нет возможности" in response_lower or "нет доступа" in response_lower or "не могу напрямую" in response_lower:
            print(f"🚫 Цензор заблокировал ответ: {response[:50]}...")
            
            # Если речь о сайтах - используем site_auditor
            if is_about_sites:
                site_auditor = context.bot_data.get('site_auditor')
                if site_auditor:
                    # Пытаемся найти URL в сообщении
                    import re
                    url_match = re.search(r'https?://[^\s]+', user_message)
                    if url_match:
                        url = url_match.group(0)
                        await update.message.reply_text(f"🕵️‍♂️ Анализирую сайт {url}...")
                        result = await site_auditor.audit_page(url)
                        if result.get('success'):
                            response = f"📋 **ОТЧЕТ ПО АУДИТУ:**\n\n{result['report']}"
                        else:
                            response = f"❌ Ошибка аудита: {result.get('error', 'Неизвестная ошибка')}"
                    else:
                        response = "✅ Я могу анализировать сайты! Отправьте мне URL или используйте команду /audit_site <url>"
                else:
                    response = "✅ Я могу анализировать сайты! Используйте команду /audit_site <url>"
                break
            
            # Если речь о соцсетях - проверяем social_media_real и запускаем анализ
            elif is_about_social:
                smm = context.bot_data.get('social_media_real')
                if smm and smm.instagram_available:
                    # Если это запрос на анализ Instagram - запускаем реальный анализ
                    if ("анализ" in user_msg_lower or "проанализ" in user_msg_lower or "статистика" in user_msg_lower) and ("инста" in user_msg_lower or "instagram" in user_msg_lower):
                        status_msg = await update.message.reply_text(f"📊 Сканирую последние 5 постов аккаунта @{smm.my_username}...")
                        
                        result = await smm.get_my_posts(limit=5)
                        
                        if result['success']:
                            posts_text = "\n---\n".join([
                                f"Post {i+1} [{p['type']}]: ❤️ {p['likes']} likes, 💬 {p['comments']} comments.\nТекст: {p['caption'][:200]}..." 
                                for i, p in enumerate(result['posts'])
                            ])
                            
                            # Формируем запрос для GPT с реальными данными
                            analysis_prompt = f"""Проанализируй состояние моего Instagram аккаунта @{smm.my_username} на основе последних постов:

{posts_text}

Дай краткий отчет:
1. Вовлеченность (лайки/комменты).
2. Качество контента (судя по текстам).
3. 3 конкретных совета, что улучшить прямо сейчас."""
                            
                            # Получаем анализ от GPT
                            ai = context.bot_data.get('ai')
                            config = context.bot_data.get('config')
                            language = db.get_user(update.effective_user.id).language if db else 'ru'
                            
                            from bot.prompts import get_system_prompt, ModeDetector
                            mode = ModeDetector.detect_mode(analysis_prompt, language)
                            system_prompt = get_system_prompt(language, mode)
                            
                            analysis_response, _ = await ai.get_response(
                                user_message=analysis_prompt,
                                system_prompt=system_prompt,
                                history=[],
                                language=language
                            )
                            
                            await status_msg.edit_text(f"📊 **АНАЛИЗ АККАУНТА @{smm.my_username}**\n\n{analysis_response}")
                            response = ""  # Пустой, т.к. уже отправили
                        else:
                            await status_msg.edit_text(f"⚠️ Не удалось прочитать посты: {result.get('error', 'Неизвестная ошибка')}")
                            response = ""
                    else:
                        # Обычный ответ для других запросов о соцсетях
                        response = f"✅ Принято! У меня есть доступ к аккаунту {smm.my_username}. Приступаю к выполнению задачи.\n\n(Анализирую данные...)"
                else:
                    response = "⚠️ Я готов приступить, но нужно проверить соединение. Напишите /social_status"
                break
            
            # Иначе - общий ответ
            else:
                response = "✅ Я готов помочь! Уточните, что именно нужно сделать."
                break
            
    # === AGENTIC ACTION EXECUTOR (Выполнение тегов) ===
    # Ищем теги вида [[ACTION: name | ARGS: "value"]]
    import re
    action_match = re.search(r'\[\[ACTION:\s*(\w+)(?:\s*\|\s*ARGS:\s*["\'](.*?)["\'])?\]\]', response)
    
    executed_action = False
    
    if action_match:
        action_name = action_match.group(1)
        action_args = action_match.group(2)
        
        # Очищаем ответ от технического тега
        clean_response = response.replace(action_match.group(0), "").strip()
        if clean_response:
             # Отправляем БЕЗ Markdown, чтобы избежать Can't parse entities
             await update.message.reply_text(clean_response)
        
        smm = context.bot_data.get('social_media_real')
        
        # 1. Обновление Био
        if action_name == 'update_bio' and action_args:
            if smm and smm.instagram_available:
                wait_msg = await update.message.reply_text("⚙️ Применяю новые настройки профиля...")
                res = await smm.update_profile(biography=action_args)
                if res['success']:
                    await wait_msg.edit_text(f"✅ Профиль успешно обновлен! Новое био установлено для {smm.my_username}.")
                else:
                    await wait_msg.edit_text(f"❌ Ошибка Instagram: {res['error']}")
            else:
                await update.message.reply_text("⚠️ Ошибка: Нет подключения к Instagram.")
                
        # 2. Анализ постов
        elif action_name == 'analyze_posts':
             if smm and smm.instagram_available:
                 status_msg = await update.message.reply_text("📊 Сканирую посты для анализа...")
                 res = await smm.get_my_posts(limit=5)
                 if res['success']:
                     posts_summary = "\n".join([f"- {p['caption'][:50]}... (❤️{p['likes']})" for p in res['posts']])
                     await status_msg.edit_text(f"✅ Данные получены:\n{posts_summary}\n\n(Здесь должен быть детальный анализ, я работаю над этим...)")
                 else:
                     await status_msg.edit_text(f"❌ Ошибка сканирования: {res['error']}")

        # 3. Проверка статуса
        elif action_name == 'check_status':
             from bot.handlers.social_commands import social_status_real_command
             await social_status_real_command(update, context)

        executed_action = True

    # Если действия не было, просто отправляем ответ (с учетом Цензора)
    if not executed_action:
        # Сохраняем в кеш
        if config.CACHE_ENABLED and model_used != 'error':
            db.set_cached_response(user_message, response, ttl=config.CACHE_TTL)
        
        await update.message.reply_text(response)
    
    # Сохраняем в историю
    db.save_message(
        telegram_id=user_id,
        user_message=original_message,
        bot_response=response,
        language=language,
        model_used=model_used or 'unknown',
        is_cached=False
    )
    
    # --- MIND SYNC: Анализ профиля ---
    if mind_sync and user.message_count % 5 == 0:
        print(f"🧠 Mind Sync: Запуск анализа для {user_id}...")
        # Получаем свежую историю (уже с текущим сообщением)
        fresh_history = db.get_user_history(user_id, limit=20)
        # Запускаем анализ (не блокируя ответ пользователю, если бы это было в фоне, но тут await)
        # В идеале это в create_task, но для надежности сейчас так
        try:
            await mind_sync.analyze_and_update_profile(user_id, fresh_history)
        except Exception as e:
            print(f"⚠️ Ошибка Mind Sync анализа: {e}")
    # ---------------------------------
    
    # Периодическая очистка кеша
    if user.message_count % 10 == 0:
        cleared = db.clear_expired_cache()
        if cleared > 0:
            print(f"🧹 Очищено {cleared} просроченных записей из кеша")


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений"""
    db = context.bot_data['db']
    ai = context.bot_data['ai']
    config = context.bot_data['config']
    
    user_id = update.effective_user.id
    
    # Получаем пользователя
    user = db.get_or_create_user(
        telegram_id=user_id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )
    
    language = user.language
    
    try:
        # Отправляем статус "печатает"
        await update.message.chat.send_action("typing")
        
        # Скачиваем голосовое сообщение
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        
        # Сохраняем временно
        temp_file = f"temp_voice_{user_id}.ogg"
        await file.download_to_drive(temp_file)
        
        # Транскрибируем
        transcribed_text = await ai.transcribe_audio(temp_file)
        
        # Удаляем временный файл
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if not transcribed_text:
            error_messages = {
                'hy': '❌ Չկարողացա ճանաչել ձայնը։ Փորձեք կրկին։',
                'ru': '❌ Не удалось распознать голос. Попробуйте еще раз.',
                'en': '❌ Could not recognize voice. Please try again.'
            }
            await update.message.reply_text(error_messages.get(language, error_messages['en']))
            return
        
        # Показываем распознанный текст
        await update.message.reply_text(f"🎤 {transcribed_text}")
        
        # Увеличиваем счетчик сообщений
        db.increment_message_count(user_id)
        
        # Определяем язык
        detected_lang = LanguageDetector.detect(transcribed_text)
        if detected_lang in ['hy', 'ru', 'en']:
            db.update_user_language(user_id, detected_lang)
            language = detected_lang
        
        # Определяем режим работы по транскрибированному тексту
        mode = ModeDetector.detect_mode(transcribed_text, language)
        
        # Загружаем системный промпт с учетом режима
        system_prompt = get_system_prompt(language, mode)
        
        # --- MIND SYNC: Адаптация под пользователя ---
        mind_sync = context.bot_data.get('mind_sync')
        if mind_sync:
            adaptive_instruction = await mind_sync.get_adaptive_instruction(user_id)
            if adaptive_instruction:
                system_prompt += adaptive_instruction
        # ---------------------------------------------
        
        # Получаем историю
        history = db.get_user_history(user_id, limit=config.MAX_CONTEXT_MESSAGES)
        
        # Получаем ответ от AI
        response, model_used = await ai.get_response(
            user_message=transcribed_text,
            system_prompt=system_prompt,
            history=history,
            language=language
        )
        
        if not response:
            fallback_messages = {
                'hy': 'Ներողություն, չկարողացա պատասխանել։',
                'ru': 'Извините, не смог ответить.',
                'en': 'Sorry, couldn\'t respond.'
            }
            response = fallback_messages.get(language, fallback_messages['en'])
            model_used = 'error'
        
        # Отправляем ответ
        await update.message.reply_text(response)
        
        # Сохраняем в историю
        db.save_message(
            telegram_id=user_id,
            user_message=transcribed_text,
            bot_response=response,
            language=language,
            model_used=model_used or 'unknown',
            is_cached=False
        )
        
        # --- MIND SYNC: Анализ профиля ---
        if mind_sync and user.message_count % 5 == 0:
            fresh_history = db.get_user_history(user_id, limit=20)
            try:
                await mind_sync.analyze_and_update_profile(user_id, fresh_history)
            except Exception as e:
                print(f"⚠️ Ошибка Mind Sync анализа (voice): {e}")
        # ---------------------------------
        
    except Exception as e:
        print(f"❌ Ошибка обработки голоса: {e}")
        error_messages = {
            'hy': '❌ Սխալ ձայնի մշակման ժամանակ։',
            'ru': '❌ Ошибка при обработке голоса.',
            'en': '❌ Error processing voice message.'
        }
        await update.message.reply_text(error_messages.get(language, error_messages['en']))


def load_system_prompt(language: str = 'hy') -> str:
    """
    Загрузка системного промпта
    
    Args:
        language: Язык промпта ('hy', 'ru', 'en')
        
    Returns:
        Системный промпт
    """
    prompts = {
        'hy': """Դու Botsi ես - խելացի AI օգնականը։

Քո առաքելությունը՝
- Պատասխանել հայերեն լեզվով
- Լինել օգտակար, ընկերական և պրոֆեսիոնալ
- Տրամադրել ճշգրիտ և հստակ տեղեկատվություն
- Օգնել օգտատերերին իրենց խնդիրների լուծման հարցում

Պատասխանիր կարճ և հստակ, եթե հարցը պարզ է։
Եթե հարցը բարդ է, տուր մանրամասն բացատրություն։""",
        
        'ru': """Ты Botsi - умный AI помощник.

Твоя миссия:
- Отвечать на русском языке
- Быть полезным, дружелюбным и профессиональным
- Предоставлять точную и четкую информацию
- Помогать пользователям решать их задачи

Отвечай кратко и ясно, если вопрос простой.
Если вопрос сложный, дай подробное объяснение.""",
        
        'en': """You are Botsi - a smart AI assistant.

Your mission:
- Respond in English
- Be helpful, friendly and professional
- Provide accurate and clear information
- Help users solve their problems

Answer briefly and clearly if the question is simple.
If the question is complex, give a detailed explanation."""
    }
    
    return prompts.get(language, prompts['en'])
