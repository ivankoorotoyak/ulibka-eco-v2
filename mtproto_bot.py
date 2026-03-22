#!/usr/bin/env python3
"""
Бот с интеграцией MTProto для расширенных функций Telegram API
Версия: 1.0
"""

import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mtproto_client import mtproto

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/var/log/smile_ecosystem/mtproto_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "🤖 *MTProto Bot*\n\n"
        "Расширенный бот с доступом к Telegram Client API.\n\n"
        "*Доступные команды:*\n"
        "🔍 `/info @username` — информация о пользователе\n"
        "💬 `/chat @chat_username` — последние сообщения из чата\n"
        "📋 `/dialogs` — список последних диалогов\n"
        "📡 `/mtproto_status` — статус MTProto подключения\n"
        "🔌 `/shutdown` — отключить MTProto клиент",
        parse_mode='Markdown'
    )


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /info @username"""
    if not context.args:
        await update.message.reply_text("❌ Укажите username: `/info @username`", parse_mode='Markdown')
        return
    
    username = context.args[0]
    await update.message.reply_text(f"🔍 Получаю информацию о {username}...")
    
    if not mtproto.is_configured():
        await update.message.reply_text(
            "❌ *MTProto не настроен*\n\n"
            "Добавьте в .env:\n"
            "`TELEGRAM_API_ID=ваш_id`\n"
            "`TELEGRAM_API_HASH=ваш_hash`\n\n"
            "Получить на https://my.telegram.org/apps",
            parse_mode='Markdown'
        )
        return
    
    user_info = await mtproto.get_user_info(username)
    if user_info:
        text = f"📋 *Информация о пользователе*\n\n"
        text += f"🆔 ID: `{user_info['id']}`\n"
        text += f"👤 Username: @{user_info['username']}\n"
        text += f"📛 Имя: {user_info['first_name']}\n"
        if user_info.get('last_name'):
            text += f"📛 Фамилия: {user_info['last_name']}\n"
        if user_info.get('phone'):
            text += f"📞 Телефон: {user_info['phone']}\n"
        text += f"🤖 Бот: {'да' if user_info.get('is_bot') else 'нет'}"
        await update.message.reply_text(text, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось получить информацию о пользователе")


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /chat @chat_username"""
    if not context.args:
        await update.message.reply_text("❌ Укажите username чата: `/chat @chat_username`", parse_mode='Markdown')
        return
    
    chat_username = context.args[0]
    await update.message.reply_text(f"💬 Получаю сообщения из {chat_username}...")
    
    if not mtproto.is_configured():
        await update.message.reply_text(
            "❌ *MTProto не настроен*\n\n"
            "Добавьте TELEGRAM_API_ID и TELEGRAM_API_HASH в .env",
            parse_mode='Markdown'
        )
        return
    
    messages = await mtproto.get_chat_messages(chat_username, limit=5)
    if messages:
        text = f"📋 *Последние сообщения из {chat_username}*\n\n"
        for i, msg in enumerate(messages[:5], 1):
            sender = msg.get('sender_name', 'unknown')
            content = msg.get('text', '[без текста]')[:100]
            text += f"{i}. *{sender}*: {content}\n"
        await update.message.reply_text(text, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось получить сообщения")


async def dialogs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /dialogs — список последних диалогов"""
    await update.message.reply_text("📋 Получаю список диалогов...")
    
    if not mtproto.is_configured():
        await update.message.reply_text("❌ MTProto не настроен")
        return
    
    dialogs = await mtproto.get_dialogs(limit=10)
    if dialogs:
        text = "*Последние диалоги:*\n\n"
        for d in dialogs:
            icon = "👤" if d['is_user'] else "👥" if d['is_group'] else "📢"
            text += f"{icon} {d['name']} (непрочитанных: {d['unread_count']})\n"
        await update.message.reply_text(text, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Не удалось получить диалоги")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /mtproto_status"""
    if mtproto.is_configured():
        api_id = mtproto.api_id
        api_hash = mtproto.api_hash
        await update.message.reply_text(
            f"✅ *MTProto настроен*\n\n"
            f"📊 API_ID: `{api_id}`\n"
            f"🔐 API_HASH: `{api_hash[:6]}...{api_hash[-4:] if api_hash else ''}`\n"
            f"🔌 Статус: {'подключён' if mtproto._connected else 'отключён'}\n\n"
            "Используйте `/info @username` для получения информации",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ *MTProto не настроен*\n\n"
            "Добавьте в .env:\n"
            "```\n"
            "TELEGRAM_API_ID=ваш_id\n"
            "TELEGRAM_API_HASH=ваш_hash\n"
            "```\n\n"
            "Получить на https://my.telegram.org/apps",
            parse_mode='Markdown'
        )


async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /shutdown — отключить MTProto"""
    await update.message.reply_text("🔌 Отключаю MTProto клиент...")
    await mtproto.disconnect()
    await update.message.reply_text("✅ MTProto клиент отключён")


async def post_init(app: Application):
    """Инициализация после запуска бота"""
    if mtproto.is_configured():
        logger.info("🔄 Подключение MTProto...")
        connected = await mtproto.connect()
        if connected:
            logger.info("✅ MTProto клиент подключён")
        else:
            logger.warning("⚠️ MTProto не подключён, проверьте настройки")
    else:
        logger.warning("⚠️ MTProto не настроен: добавьте TELEGRAM_API_ID и TELEGRAM_API_HASH в .env")


def main():
    token = os.getenv("MTPROTO_BOT_TOKEN")
    if not token:
        logger.error("❌ MTPROTO_BOT_TOKEN не задан в .env")
        logger.info("📌 Создайте бота @BotFather: /newbot → @mtproto_ulibka_bot")
        logger.info("📌 Добавьте токен в .env: MTPROTO_BOT_TOKEN=токен")
        return
    
    app = Application.builder().token(token).build()
    
    # Регистрация команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("chat", chat_command))
    app.add_handler(CommandHandler("dialogs", dialogs_command))
    app.add_handler(CommandHandler("mtproto_status", status_command))
    app.add_handler(CommandHandler("shutdown", shutdown_command))
    
    # Инициализация после запуска
    app.post_init = post_init
    
    logger.info("🤖 MTProto Bot запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
