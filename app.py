import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
AGE, ROLE, WORK_SAMPLES, TG_LINK = range(4)

# Получаем конфигурацию из переменных окружения
BOT_TOKEN = os.getenv(8203079776:AAG_USH_fnsxFStBChpEkR9plsLBpMp_2jQ)
ADMIN_CHAT_ID = os.getenv(5009120278)

# Клавиатура для выбора роли
role_keyboard = [
    ['Перевод япон', 'Перевод англ'],
    ['Монтажер', 'Звукомонтажер'],
    ['Актёр озвучки', 'Актриса озвучки']
]
reply_markup = ReplyKeyboardMarkup(role_keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает разговор и спрашивает возраст."""
    await update.message.reply_text(
        "Добро пожаловать в кастинг-студию Aniframe! 🎙️\n\n"
        "Ответьте на несколько вопросов для участия в кастинге.\n\n"
        "Сколько вам лет?",
        reply_markup=ReplyKeyboardRemove()
    )
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет возраст и спрашивает о роли."""
    context.user_data['age'] = update.message.text
    await update.message.reply_text(
        "Кем вы хотите быть в нашей студии?",
        reply_markup=reply_markup
    )
    return ROLE

async def role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет роль и запрашивает работы или переходит к следующему шагу."""
    role = update.message.text
    context.user_data['role'] = role
    
    if role in ['Перевод япон', 'Перевод англ']:
        context.user_data['work_samples'] = 'Не требуется (переводчик)'
        await update.message.reply_text(
            "Пришлите ссылку на ваш Telegram аккаунт (например: @username)\n\n"
            "Если вы нам подходите, администратор свяжется с вами.",
            reply_markup=ReplyKeyboardRemove()
        )
        return TG_LINK
    else:
        await update.message.reply_text(
            "Пришлите примеры ваших работ (фото, видео, аудио или документы)\n\n"
            "Отправьте файлы, затем напишите /done чтобы продолжить",
            reply_markup=ReplyKeyboardRemove()
        )
        return WORK_SAMPLES

async def work_samples(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет примеры работ."""
    if 'work_samples' not in context.user_data:
        context.user_data['work_samples'] = []
    
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        context.user_data['work_samples'].append({'type': 'photo', 'file_id': file_id})
        await update.message.reply_text("✅ Фото сохранено! Отправьте еще или /done")
    elif update.message.video:
        file_id = update.message.video.file_id
        context.user_data['work_samples'].append({'type': 'video', 'file_id': file_id})
        await update.message.reply_text("✅ Видео сохранено! Отправьте еще или /done")
    elif update.message.audio:
        file_id = update.message.audio.file_id
        context.user_data['work_samples'].append({'type': 'audio', 'file_id': file_id})
        await update.message.reply_text("✅ Аудио сохранено! Отправьте еще или /done")
    elif update.message.document:
        file_id = update.message.document.file_id
        context.user_data['work_samples'].append({'type': 'document', 'file_id': file_id})
        await update.message.reply_text("✅ Документ сохранен! Отправьте еще или /done")
    
    return WORK_SAMPLES

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершает отправку работ."""
    if 'work_samples' not in context.user_data or not context.user_data['work_samples']:
        await update.message.reply_text("❌ Вы не отправили работы. Отправьте хотя бы один файл.")
        return WORK_SAMPLES
    
    await update.message.reply_text(
        "Пришлите ссылку на ваш Telegram аккаунт (например: @username)\n\n"
        "Если вы нам подходите, администратор свяжется с вами.",
        reply_markup=ReplyKeyboardRemove()
    )
    return TG_LINK

async def tg_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет ссылку и отправляет заявку."""
    context.user_data['tg_link'] = update.message.text
    user = update.message.from_user
    
    application_text = f"""
🎬 НОВАЯ ЗАЯВКА В ANIFRAME

👤 Пользователь: {user.first_name}
🔞 Возраст: {context.user_data['age']}
🎭 Роль: {context.user_data['role']}
📎 Работ: {len(context.user_data.get('work_samples', []))}
📞 Telegram: {context.user_data['tg_link']}
🆔 ID: {user.id}
    """
    
    try:
        await context.bot.send_message(ADMIN_CHAT_ID, application_text)
        
        # Отправляем работы администратору
        if 'work_samples' in context.user_data:
            for work in context.user_data['work_samples']:
                try:
                    if work['type'] == 'photo':
                        await context.bot.send_photo(ADMIN_CHAT_ID, work['file_id'])
                    elif work['type'] == 'video':
                        await context.bot.send_video(ADMIN_CHAT_ID, work['file_id'])
                    elif work['type'] == 'audio':
                        await context.bot.send_audio(ADMIN_CHAT_ID, work['file_id'])
                    elif work['type'] == 'document':
                        await context.bot.send_document(ADMIN_CHAT_ID, work['file_id'])
                except:
                    continue
        
        await update.message.reply_text("✅ Заявка отправлена! Администратор свяжется с вами.")
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("❌ Ошибка при отправке заявки.")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет разговор."""
    await update.message.reply_text("Заявка отменена.")
    context.user_data.clear()
    return ConversationHandler.END

def main():
    """Запуск бота."""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен!")
        return
    if not ADMIN_CHAT_ID:
        logger.error("❌ ADMIN_CHAT_ID не установлен!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            ROLE: [MessageHandler(filters.Regex('^(Перевод япон|Перевод англ|Монтажер|Звукомонтажер|Актёр озвучки|Актриса озвучки)$'), role)],
            WORK_SAMPLES: [
                MessageHandler(filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.DOCUMENT, work_samples),
                CommandHandler('done', done)
            ],
            TG_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, tg_link)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Для вебхуков (на хостинге) или polling (локально)
    if os.getenv('WEBHOOK_URL'):
        # Режим вебхука для хостинга
        webhook_url = os.getenv('WEBHOOK_URL')
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv('PORT', 8443)),
            url_path=BOT_TOKEN,
            webhook_url=webhook_url
        )
    else:
        # Режим polling для локального тестирования
        application.run_polling()

if __name__ == '__main__':
    main()
