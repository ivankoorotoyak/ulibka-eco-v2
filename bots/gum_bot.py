"""GumBot - бот для лечения десен"""

import asyncio
import logging
from telegram.ext import Application, CommandHandler

logger = logging.getLogger(__name__)


class GumBot:
    """Бот для лечения десен"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = None
        logger.info(f"GumBot инициализирован с токеном: {token[:10]}...")
    
    async def _register_handlers(self):
        """Регистрация обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        logger.info("Обработчики GumBot зарегистрированы")
    
    async def cmd_start(self, update, context):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "🦷 Здравствуйте! Я бот для лечения десен.\n\n"
            "Доступные команды:\n"
            "/help - помощь"
        )
    
    async def cmd_help(self, update, context):
        """Обработчик команды /help"""
        await update.message.reply_text(
            "🦷 Бот для лечения десен поможет вам:\n"
            "- Получить консультацию\n"
            "- Записаться на прием\n"
            "- Узнать о профилактике"
        )
    
    async def run(self):
        """Запуск бота с блокирующим ожиданием"""
        logger.info("Запуск GumBot...")
        self.application = Application.builder().token(self.token).build()
        await self._register_handlers()
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("✅ GumBot запущен и готов к работе")
        await asyncio.Event().wait()
