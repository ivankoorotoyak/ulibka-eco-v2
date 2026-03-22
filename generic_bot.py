#!/usr/bin/env python3
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = sys.argv[1] if len(sys.argv) > 1 else "NO_TOKEN"
BOT_NAME = sys.argv[2] if len(sys.argv) > 2 else "Bot"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'/var/log/{BOT_NAME}.log'),
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
    if TOKEN == "NO_TOKEN":
        logger.error("Токен не указан!")
        sys.exit(1)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info(f"✅ {BOT_NAME} запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

# Добавление rate limiting в начало файла
from rate_limiter import rate_limit


class BaseBot:
    """Базовый класс для всех ботов (обновлённый)"""
    
    # ... существующий код ...
    
    @rate_limit(max_calls=10, time_window=60, cooldown_message="⏳ Слишком много команд. Подождите минуту.")
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start с rate limiting"""
        user = update.effective_user
        self.logger.info(f"User {user.id} started bot")
        await update.message.reply_text(self._get_welcome_message(user.first_name), parse_mode=ParseMode.HTML)
    
    @rate_limit(max_calls=10, time_window=60)
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help с rate limiting"""
        await update.message.reply_text(self._get_help_message(), parse_mode=ParseMode.HTML)
    
    @rate_limit(max_calls=5, time_window=60)
    async def cmd_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /info с rate limiting"""
        await update.message.reply_text(self._get_info_message(), parse_mode=ParseMode.HTML)
