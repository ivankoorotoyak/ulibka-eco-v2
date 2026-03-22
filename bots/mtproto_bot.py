"""MtprotoBot - бот для MTProto прокси"""

import asyncio
import logging
from telegram.ext import Application, CommandHandler

logger = logging.getLogger(__name__)


class MtprotoBot:
    def __init__(self, token: str):
        self.token = token
        self.application = None
    
    async def _register_handlers(self):
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("renew", self.cmd_renew))
        logger.info("Обработчики MtprotoBot зарегистрированы")
    
    async def cmd_start(self, update, context):
        await update.message.reply_text(
            "🚀 MTProto Proxy Bot\n\n"
            "Доступные команды:\n"
            "/status - статус прокси\n"
            "/renew - продлить подписку"
        )
    
    async def cmd_status(self, update, context):
        await update.message.reply_text("✅ Прокси работает стабильно")
    
    async def cmd_renew(self, update, context):
        await update.message.reply_text("🔑 Для продления обратитесь к администратору")
    
    async def run(self):
        self.application = Application.builder().token(self.token).build()
        await self._register_handlers()
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info(f"✅ MtprotoBot запущен")
        await asyncio.Event().wait()
