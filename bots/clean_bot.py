"""Dentai Bot - основной бот стоматологической клиники"""

import logging
from telegram.ext import CommandHandler, MessageHandler, filters
from .base_bot import BaseBot

logger = logging.getLogger(__name__)


class CleanBotBot(BaseBot):
    """Бот для стоматологической клиники Dentai"""
    
    async def _register_handlers(self) -> None:
        """Регистрация обработчиков"""
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("appointment", self.cmd_appointment))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)
        logger.info("Обработчики CleanBotBot зарегистрированы")
    
    async def cmd_start(self, update, context):
        await update.message.reply_text(
            "👋 Здравствуйте! Я бот стоматологической клиники Dentai.\n\n"
            "Доступные команды:\n"
            "/help - помощь\n"
            "/appointment - записаться на прием"
        )
    
    async def cmd_help(self, update, context):
        await update.message.reply_text(
            "🦷 Помощь:\n"
            "/start - приветствие\n"
            "/appointment - запись на прием\n\n"
            "Или просто напишите сообщение"
        )
    
    async def cmd_appointment(self, update, context):
        await update.message.reply_text(
            "📅 Запись на прием:\n\n"
            "Отправьте ваше имя, желаемую дату и время.\n"
            "Пример: Иван Иванов, 25 марта, 15:00"
        )
        return "AWAITING_APPOINTMENT"
    
    async def handle_message(self, update, context):
        text = update.message.text
        await update.message.reply_text(
            f"✅ Заявка принята!\n\n"
            f"Ваше сообщение: {text}\n\n"
            f"Администратор свяжется с вами."
        )
        logger.info(f"Заявка от {update.effective_user.id}: {text}")
    
    async def error_handler(self, update, context):
        logger.error(f"Ошибка: {context.error}", exc_info=context.error)
        if update and update.effective_message:
            await update.effective_message.reply_text("⚠️ Ошибка, попробуйте позже.")

    async def run(self):
        self.application = Application.builder().token(self.token).build()
        await self._register_handlers()
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info(f"✅ {self.__class__.__name__} запущен")
        await asyncio.Event().wait()
