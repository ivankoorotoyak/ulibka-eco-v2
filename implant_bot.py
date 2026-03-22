#!/usr/bin/env python3
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_NAME = "implant_bot"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'/var/log/implant_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 *{BOT_NAME}*\n\n"
        f"Бот запущен и готов к работе!\n\n"
        f"📋 *Команды:*\n"
        f"/start - приветствие\n"
        f"/help - помощь\n"
        f"/info - информация о боте",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📋 *Помощь по боту {BOT_NAME}*\n\n"
        f"Доступные команды:\n"
        f"/start - показать приветствие\n"
        f"/help - показать эту справку\n"
        f"/info - информация о версии",
        parse_mode='Markdown'
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"ℹ️ *Информация о боте*\n\n"
        f"Имя: {BOT_NAME}\n"
        f"Версия: 1.0\n"
        f"Статус: ✅ активен\n"
        f"Режим: long polling",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📝 Сообщение получено.\n\n"
        f"Используйте /help для списка команд."
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info(f"✅ {BOT_NAME} запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
