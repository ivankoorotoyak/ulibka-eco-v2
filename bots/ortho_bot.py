"""OrthoBot - бот для ортодонтии"""

import logging
from telegram.ext import CommandHandler, MessageHandler, filters
from .base_bot import BaseBot

logger = logging.getLogger(__name__)


class OrthoBot(BaseBot):
    """Бот для ортодонтического лечения"""
    
    async def _register_handlers(self) -> None:
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("braces", self.cmd_braces))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)
        logger.info("Обработчики OrthoBot зарегистрированы")
    
    async def cmd_start(self, update, context):
        await update.message.reply_text(
            "🦷 Ортодонтия Улыбка\n\n"
            "Красивая улыбка - наша миссия!\n"
            "/braces - консультация по брекетам"
        )
    
    async def cmd_help(self, update, context):
        await update.message.reply_text(
            "Доступные команды:\n"
            "/start - приветствие\n"
            "/braces - консультация по брекетам"
        )
    
    async def cmd_braces(self, update, context):
        await update.message.reply_text(
            "🦷 Консультация ортодонта:\n"
            "Отправьте ваш вопрос, и наш специалист ответит в ближайшее время."
        )
    
    async def handle_message(self, update, context):
        text = update.message.text
        await update.message.reply_text(
            f"✅ Вопрос принят!\n\n"
            f"Ортодонт свяжется с вами."
        )
        logger.info(f"Заявка OrthoBot от {update.effective_user.id}")
    
    async def error_handler(self, update, context):
        logger.error(f"OrthoBot ошибка: {context.error}")
