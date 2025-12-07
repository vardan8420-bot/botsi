"""
Команды управления автономным режимом
"""
from telegram import Update
from telegram.ext import ContextTypes


SETTING_KEY = "AUTONOMY_ENABLED"


async def autonomy_on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data.get('db')
    if not db:
        await update.message.reply_text("⚠️ БД недоступна")
        return
    db.set_setting(SETTING_KEY, "true")
    context.application.bot_data['autonomy_enabled'] = True
    await update.message.reply_text("✅ Автономный режим включен. Задачи будут выполняться фоново.")


async def autonomy_off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data.get('db')
    if not db:
        await update.message.reply_text("⚠️ БД недоступна")
        return
    db.set_setting(SETTING_KEY, "false")
    context.application.bot_data['autonomy_enabled'] = False
    await update.message.reply_text("⏸️ Автономный режим выключен. Фоновые публикации остановлены.")


async def autonomy_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data.get('db')
    if not db:
        await update.message.reply_text("⚠️ БД недоступна")
        return
    val = db.get_setting(SETTING_KEY, default="false") or "false"
    enabled = (val.lower() == "true")
    await update.message.reply_text(
        f"🤖 Автономный режим: {'✅ ВКЛ' if enabled else '❌ ВЫКЛ'}"
    )