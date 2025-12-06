"""
Команды AI разработчика (Этап 4)
"""
from telegram import Update
from telegram.ext import ContextTypes


async def generate_code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /generate_code <язык> <описание>"""
    code_gen = context.bot_data.get('code_generator')
    
    if not code_gen:
        await update.message.reply_text("❌ Генератор кода недоступен")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "💻 Использование: /generate_code <язык> <описание>\n\n"
            "Языки: python, javascript, typescript, java, go, rust\n\n"
            "Пример: /generate_code python Функция для сортировки списка"
        )
        return
    
    language = context.args[0].lower()
    description = ' '.join(context.args[1:])
    
    await update.message.reply_text("⏳ Генерирую код...")
    
    code = await code_gen.generate_code(description, language)
    
    if code:
        # Отправляем код с форматированием
        await update.message.reply_text(f"```{language}\n{code}\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось сгенерировать код")


async def analyze_code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /analyze_code - анализ кода из сообщения"""
    code_gen = context.bot_data.get('code_generator')
    
    if not code_gen:
        await update.message.reply_text("❌ Генератор кода недоступен")
        return
    
    # Проверяем есть ли ответ на сообщение с кодом
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text(
            "💻 Ответьте на сообщение с кодом командой /analyze_code\n\n"
            "Или используйте: /analyze_code <язык>\n"
            "И отправьте код следующим сообщением"
        )
        return
    
    code = update.message.reply_to_message.text
    language = context.args[0] if context.args else 'python'
    
    await update.message.reply_text("⏳ Анализирую код...")
    
    analysis = await code_gen.analyze_code(code, language)
    
    if analysis:
        message = f"""📊 **Анализ кода:**

⭐ Качество: {analysis.get('quality_score', 'N/A')}/10

🐛 **Потенциальные баги:**
"""
        for bug in analysis.get('bugs', []):
            message += f"• {bug}\n"
        
        message += "\n🔒 **Безопасность:**\n"
        for sec in analysis.get('security', []):
            message += f"• {sec}\n"
        
        message += "\n⚡ **Производительность:**\n"
        for perf in analysis.get('performance', []):
            message += f"• {perf}\n"
        
        message += "\n📋 **Best Practices:**\n"
        for bp in analysis.get('best_practices', []):
            message += f"• {bp}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось проанализировать код")


async def fix_code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /fix_code <проблема> - исправление кода"""
    code_gen = context.bot_data.get('code_generator')
    
    if not code_gen:
        await update.message.reply_text("❌ Генератор кода недоступен")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text(
            "💻 Ответьте на сообщение с кодом командой:\n"
            "/fix_code <описание проблемы>"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите проблему: /fix_code <описание проблемы>"
        )
        return
    
    code = update.message.reply_to_message.text
    issue = ' '.join(context.args)
    language = 'python'  # По умолчанию
    
    await update.message.reply_text("⏳ Исправляю код...")
    
    fixed_code = await code_gen.fix_code(code, issue, language)
    
    if fixed_code:
        await update.message.reply_text(f"```{language}\n{fixed_code}\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось исправить код")


async def explain_code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /explain_code - объяснение кода"""
    code_gen = context.bot_data.get('code_generator')
    
    if not code_gen:
        await update.message.reply_text("❌ Генератор кода недоступен")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text(
            "💻 Ответьте на сообщение с кодом командой /explain_code"
        )
        return
    
    code = update.message.reply_to_message.text
    language = context.args[0] if context.args else 'python'
    
    await update.message.reply_text("⏳ Объясняю код...")
    
    explanation = await code_gen.explain_code(code, language)
    
    if explanation:
        await update.message.reply_text(explanation)
    else:
        await update.message.reply_text("❌ Не удалось объяснить код")


async def refactor_code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /refactor_code - рефакторинг кода"""
    code_gen = context.bot_data.get('code_generator')
    
    if not code_gen:
        await update.message.reply_text("❌ Генератор кода недоступен")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text(
            "💻 Ответьте на сообщение с кодом командой /refactor_code"
        )
        return
    
    code = update.message.reply_to_message.text
    language = context.args[0] if context.args else 'python'
    
    await update.message.reply_text("⏳ Рефакторю код...")
    
    refactored = await code_gen.refactor_code(code, language)
    
    if refactored:
        await update.message.reply_text(f"```{language}\n{refactored}\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось отрефакторить код")


async def generate_tests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /generate_tests - генерация тестов"""
    code_gen = context.bot_data.get('code_generator')
    
    if not code_gen:
        await update.message.reply_text("❌ Генератор кода недоступен")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text(
            "💻 Ответьте на сообщение с кодом командой /generate_tests"
        )
        return
    
    code = update.message.reply_to_message.text
    language = context.args[0] if context.args else 'python'
    
    await update.message.reply_text("⏳ Генерирую тесты...")
    
    tests = await code_gen.generate_tests(code, language)
    
    if tests:
        await update.message.reply_text(f"```{language}\n{tests}\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось сгенерировать тесты")


async def github_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /github_status - статус GitHub интеграции"""
    github = context.bot_data.get('github_manager')
    
    if not github:
        await update.message.reply_text("❌ GitHub менеджер недоступен")
        return
    
    if github.is_configured():
        message = """✅ **GitHub интеграция настроена**

Доступные функции:
• Создание репозиториев
• Создание файлов
• Pull Requests

⚠️ Функционал в разработке"""
    else:
        message = """⚠️ **GitHub не настроен**

Для активации добавьте в переменные окружения:
`GITHUB_TOKEN=your_github_personal_access_token`

Как получить token:
1. GitHub → Settings → Developer settings
2. Personal access tokens → Generate new token
3. Выберите нужные права (repo, workflow)"""
    
    await update.message.reply_text(message, parse_mode='Markdown')
