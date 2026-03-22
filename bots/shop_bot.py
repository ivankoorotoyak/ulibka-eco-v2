"""ShopBot - бот для магазина товаров"""

import logging
from telegram.ext import CommandHandler, MessageHandler, filters
from .base_bot import BaseBot

logger = logging.getLogger(__name__)


class ShopBot(BaseBot):
    """Бот для магазина стоматологических товаров"""
    
    async def _register_handlers(self) -> None:
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("catalog", self.cmd_catalog))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)
        logger.info("Обработчики ShopBot зарегистрированы")
    
    async def cmd_start(self, update, context):
        await update.message.reply_text(
            "🛍️ Магазин Улыбка\n\n"
            "Товары для здоровья зубов!\n"
            "/catalog - каталог товаров"
        )
    
    async def cmd_help(self, update, context):
        await update.message.reply_text(
            "Доступные команды:\n"
            "/start - приветствие\n"
            "/catalog - каталог товаров"
        )
    
    async def cmd_catalog(self, update, context):
        await update.message.reply_text(
            "📦 Каталог товаров:\n"
            "1. Электрические щетки\n"
            "2. Ирригаторы\n"
            "3. Отбеливающие полоски\n\n"
            "Напишите номер товара для заказа."
        )
    
    async def handle_message(self, update, context):
        text = update.message.text
        await update.message.reply_text(
            f"✅ Заказ принят!\n\n"
            f"Менеджер свяжется с вами."
        )
        logger.info(f"Заказ ShopBot от {update.effective_user.id}")
    
    async def error_handler(self, update, context):
        logger.error(f"ShopBot ошибка: {context.error}")
