"""StarsBot - бот для звездной тематики"""

import asyncio
import logging
from telegram.ext import Application, CommandHandler

logger = logging.getLogger(__name__)


class StarsBot:
    def __init__(self, token: str):
        self.token = token
        self.application = None
    
    async def _register_handlers(self):
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("stars", self.cmd_stars))
        logger.info("Обработчики StarsBot зарегистрированы")
    
    async def cmd_start(self, update, context):
        await update.message.reply_text(
            "⭐ Здравствуйте! Я бот звездной тематики.\n\n"
            "Доступные команды:\n"
            "/stars - факты о звездах\n"
            "/help - помощь"
        )
    
    async def cmd_help(self, update, context):
        await update.message.reply_text("✨ Используйте /stars для получения интересных фактов о звездах!")
    
    async def cmd_stars(self, update, context):
        await update.message.reply_text("⭐ Звезды — это огромные светящиеся шары плазмы. Наше Солнце — тоже звезда!")
    
    async def run(self):
        self.application = Application.builder().token(self.token).build()
        await self._register_handlers()
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info(f"✅ StarsBot запущен")
        await asyncio.Event().wait()
