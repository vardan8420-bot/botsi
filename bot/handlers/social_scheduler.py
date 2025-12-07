"""
Команды и воркер для автопостинга в соцсети
"""
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes


def _parse_datetime(dt_str_date: str, dt_str_time: str) -> Optional[datetime]:
    """Простой парсер даты и времени в формате YYYY-MM-DD HH:MM"""
    try:
        return datetime.strptime(f"{dt_str_date} {dt_str_time}", "%Y-%m-%d %H:%M")
    except Exception:
        return None


async def schedule_instagram_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда: /schedule_instagram YYYY-MM-DD HH:MM <caption> (ответом на фото)"""
    db = context.bot_data.get('db')
    if not db:
        await update.message.reply_text("⚠️ БД недоступна")
        return

    social = context.bot_data.get('social_media_real')
    if not social or not social.instagram_available:
        await update.message.reply_text("⚠️ Instagram недоступен. Проверьте сессию/логин.")
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "💡 Использование:\n1) Отправьте фото\n2) Ответьте на него: /schedule_instagram YYYY-MM-DD HH:MM <текст>"
        )
        return

    if len(context.args) < 3:
        await update.message.reply_text("❌ Укажите время и текст: /schedule_instagram 2025-12-07 18:30 Текст поста")
        return

    date_str, time_str = context.args[0], context.args[1]
    caption = ' '.join(context.args[2:])

    scheduled_at = _parse_datetime(date_str, time_str)
    if not scheduled_at:
        await update.message.reply_text("❌ Неверный формат даты/времени. Пример: 2025-12-07 18:30")
        return

    # Получаем file_id фото
    photo = update.message.reply_to_message.photo[-1]
    file_id = photo.file_id

    task = db.add_scheduled_post(
        platform='Instagram',
        caption=caption,
        scheduled_at=scheduled_at,
        created_by=update.effective_user.id,
        telegram_file_id=file_id,
    )

    await update.message.reply_text(
        f"✅ Запланировано (ID: {task.id}) на {scheduled_at:%Y-%m-%d %H:%M}."
    )


async def list_posts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data.get('db')
    if not db:
        await update.message.reply_text("⚠️ БД недоступна")
        return
    tasks = db.list_pending_scheduled_posts(limit=20)
    if not tasks:
        await update.message.reply_text("🟢 Очередь пуста")
        return
    lines = [
        f"#{t.id} • {t.platform} • {t.scheduled_at:%Y-%m-%d %H:%M} • {t.status}"
        for t in tasks
    ]
    await update.message.reply_text("📋 Очередь:\n" + "\n".join(lines))


async def post_now_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрая публикация: ответьте на фото и укажите подпись"""
    social = context.bot_data.get('social_media_real')
    if not social or not social.instagram_available:
        await update.message.reply_text("⚠️ Instagram недоступен")
        return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("💡 Использование: ответьте на фото командой /post_now <подпись>")
        return
    if not context.args:
        await update.message.reply_text("❌ Укажите подпись")
        return
    caption = ' '.join(context.args)
    photo = update.message.reply_to_message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    tmp_path = f"temp_postnow_{update.effective_user.id}.jpg"
    await file.download_to_drive(tmp_path)
    await update.message.reply_text("🚀 Публикую...")
    result = await social.post_instagram(caption, tmp_path)
    import os
    if os.path.exists(tmp_path):
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    if result.get('success'):
        await update.message.reply_text(f"✅ Опубликовано: {result.get('url')}")
    else:
        await update.message.reply_text(f"❌ {result.get('error')}")


async def autopost_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data.get('db')
    if not db:
        await update.message.reply_text("⚠️ БД недоступна")
        return

    stats = db.get_autopost_stats()
    await update.message.reply_text(
        "📅 Автопостинг статус:\n"
        f"Всего: {stats['total']}\n"
        f"Ожидают: {stats['pending']}\n"
        f"Опубликовано: {stats['posted']}\n"
        f"Ошибки: {stats['failed']}"
    )


async def cancel_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data.get('db')
    if not db:
        await update.message.reply_text("⚠️ БД недоступна")
        return

    if not context.args:
        await update.message.reply_text("💡 Использование: /cancel_post <id>")
        return

    try:
        task_id = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Укажите корректный ID")
        return

    ok = db.cancel_scheduled_post(task_id)
    await update.message.reply_text("✅ Отменено" if ok else "❌ Не найдено")


async def scheduled_posts_worker(context: ContextTypes.DEFAULT_TYPE):
    """Фоновый воркер: публикует задачи, у которых наступило время"""
    application = context.application
    db = application.bot_data.get('db')
    social = application.bot_data.get('social_media_real')
    bot = application.bot

    if not db or not social:
        return
    # Проверяем автономный режим
    val = db.get_setting("AUTONOMY_ENABLED", default="false") or "false"
    if val.lower() != "true":
        return

    from datetime import datetime as dt
    now_dt = dt.now().astimezone() if hasattr(dt.now(), 'astimezone') else dt.now()

    tasks = db.get_due_scheduled_posts(now_dt=now_dt, limit=3)
    for task in tasks:
        try:
            if task.platform == 'Instagram':
                if not social.instagram_available:
                    db.mark_scheduled_post_result(task.id, 'failed', error='Instagram недоступен')
                    continue

                if not task.telegram_file_id:
                    db.mark_scheduled_post_result(task.id, 'failed', error='Нет фото для Instagram')
                    continue

                # Скачиваем фото из Telegram во временный файл
                file = await bot.get_file(task.telegram_file_id)
                tmp_path = f"temp_autopost_{task.id}.jpg"
                await file.download_to_drive(tmp_path)

                result = await social.post_instagram(task.caption, tmp_path)

                # Удаление временного файла
                import os
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

                if result.get('success'):
                    db.mark_scheduled_post_result(task.id, 'posted', error=None)
                else:
                    db.mark_scheduled_post_result(task.id, 'failed', error=result.get('error'))

            elif task.platform == 'Facebook':
                if not social.facebook_available:
                    db.mark_scheduled_post_result(task.id, 'failed', error='Facebook недоступен')
                    continue
                result = await social.post_facebook(task.caption)
                if result.get('success'):
                    db.mark_scheduled_post_result(task.id, 'posted', error=None)
                else:
                    db.mark_scheduled_post_result(task.id, 'failed', error=result.get('error'))
            else:
                db.mark_scheduled_post_result(task.id, 'failed', error='Неизвестная платформа')

        except Exception as e:
            db.mark_scheduled_post_result(task.id, 'failed', error=str(e))