"""FamilyBot - бот для семейных пациентов"""

import logging
from telegram.ext import CommandHandler, MessageHandler, filters
from .base_bot import BaseBot

logger = logging.getLogger(__name__)


class FamilyBot(BaseBot):
    """Бот для семейной стоматологии"""
    
    async def _register_handlers(self) -> None:
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("appointment", self.cmd_appointment))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)
        logger.info("Обработчики FamilyBot зарегистрированы")
    
    async def cmd_start(self, update, context):
        await update.message.reply_text(
            "👨‍👩‍👧‍👦 Семейная стоматология Улыбка\n\n"
            "Мы заботимся о здоровье всей семьи!\n"
            "/appointment - записаться на прием"
        )
    
    async def cmd_help(self, update, context):
        await update.message.reply_text(
            "Доступные команды:\n"
            "/start - приветствие\n"
            "/appointment - запись на прием"
        )
    
    async def cmd_appointment(self, update, context):
        await update.message.reply_text(
            "📅 Запись на прием:\n"
            "Отправьте: Имя, дата, время\n"
            "Пример: Иванова семья, 25 марта, 15:00"
        )
    
    async def handle_message(self, update, context):
        text = update.message.text
        await update.message.reply_text(
            f"✅ Заявка принята!\n\n"
            f"Семейный врач свяжется с вами."
        )
        logger.info(f"Заявка FamilyBot от {update.effective_user.id}")
    
    async def error_handler(self, update, context):
        logger.error(f"FamilyBot ошибка: {context.error}")
