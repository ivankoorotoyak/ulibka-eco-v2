#!/usr/bin/env python3
"""
БОТЫ ЭКОСИСТЕМЫ "ВСЕЛЕННАЯ УЛЫБКА"
Версия: 6.6 — исправленная с блокирующим run()
"""

import os
import logging
import asyncio
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode


class BotPersonality(Enum):
    PROF = "profmedical"
    DENTAI = "dentai_smile"
    DENTAI_HELP = "dentai_help"
    DREAM = "dream_smile"
    INCLUSIVE = "ulibka_inclusive"
    KARTA = "vanxo2030"
    ADMIN = "vanxoadmin"
    CLEAN = "hygiene_ulibka"
    JOKE = "ulibka_joke"
    IMPLANT = "stomvrn"
    KID = "ulibka_kid"
    PHILO = "ulibka_philo"
    FAMILY = "family"
    ORTHO = "ortho"
    SHOP = "shop"
    AI_AGENT = "ai_agent"


@dataclass
class UserState:
    user_id: int
    username: str = ""
    first_name: str = ""
    last_active: float = field(default_factory=time.time)
    data: Dict = field(default_factory=dict)


class BaseBot:
    def __init__(self, token: str, personality: BotPersonality, name: str):
        self.token = token
        self.personality = personality
        self.name = name
        self._setup_logging()
        self.application = None
    
    def _setup_logging(self):
        log_dir = Path("/var/log/smile_ecosystem")
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format=f'%(asctime)s - {self.name} - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"{self.name}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.name)
    
    def get_application(self) -> Application:
        if self.application is None:
            self.application = Application.builder().token(self.token).build()
            self._register_handlers(self.application)
        return self.application
    
    def _register_handlers(self, app: Application):
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("info", self.cmd_info))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.logger.info(f"User {user.id} started bot")
        await update.message.reply_text(self._get_welcome_message(user.first_name), parse_mode=ParseMode.HTML)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self._get_help_message(), parse_mode=ParseMode.HTML)
    
    async def cmd_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self._get_info_message(), parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"👋 <b>Привет, {name}!</b>\n\nЯ {self.name}.\n\n/help — список команд"
    
    def _get_help_message(self) -> str:
        return f"🤖 <b>{self.name}</b>\n\n/start — начать\n/help — помощь\n/info — информация"
    
    def _get_info_message(self) -> str:
        return f"📊 <b>{self.name}</b>\nВерсия: 6.6\nСтатус: активен"
    
    async def run(self):
        """Блокирующий запуск бота"""
        app = self.get_application()
        self.logger.info(f"Starting {self.name}...")
        await app.run_polling()


class ProfBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.PROF, "prof_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("fact", self.cmd_fact))
    
    async def cmd_fact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        facts = ["🧠 Мозг содержит 86 млрд нейронов", "🔬 Тело состоит из 37 трлн клеток"]
        await update.message.reply_text(f"📖 <b>Научный факт</b>\n\n{random.choice(facts)}", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🎓 <b>Привет, {name}!</b>\n\nЯ <b>ProfBot</b> — научный помощник.\n\n/fact — научный факт\n/help — помощь"


class AdminBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.ADMIN, "admin_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("stats", self.cmd_stats))
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📊 <b>Статистика</b>\n\n15 ботов активны", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"⚙️ <b>Привет, {name}!</b>\n\nЯ <b>AdminBot</b>.\n\n/stats — статистика\n/help — помощь"


class CleanBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.CLEAN, "clean_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("hygiene", self.cmd_hygiene))
    
    async def cmd_hygiene(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🧼 <b>Гигиена</b>\n\nМойте руки перед едой", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🧼 <b>Привет, {name}!</b>\n\nЯ <b>CleanBot</b>.\n\n/hygiene — гигиена\n/help — помощь"


class DentaiBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.DENTAI, "dentai_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("care", self.cmd_care))
    
    async def cmd_care(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🦷 <b>Уход за зубами</b>\n\nЧистите зубы 2 раза в день", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🦷 <b>Привет, {name}!</b>\n\nЯ <b>DentaiBot</b>.\n\n/care — уход\n/help — помощь"


class DentaiHelpBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.DENTAI_HELP, "dentai_help_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("symptoms", self.cmd_symptoms))
    
    async def cmd_symptoms(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🩺 <b>Симптомы</b>\n\nБоль в зубе — обратитесь к стоматологу", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🦷 <b>Привет, {name}!</b>\n\nЯ <b>DentaiHelpBot</b>.\n\n/symptoms — симптомы\n/help — помощь"


class DreamBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.DREAM, "dream_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("interpret", self.cmd_interpret))
    
    async def cmd_interpret(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🌙 <b>Сны</b>\n\nОпишите сон — я помогу интерпретировать", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🌙 <b>Привет, {name}!</b>\n\nЯ <b>DreamBot</b>.\n\n/interpret — сны\n/help — помощь"


class FamilyBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.FAMILY, "family_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("family", self.cmd_family))
    
    async def cmd_family(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👨‍👩‍👧‍👦 <b>Семья</b>\n\nВремя вместе — лучший подарок", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"👨‍👩‍👧‍👦 <b>Привет, {name}!</b>\n\nЯ <b>FamilyBot</b>.\n\n/family — семья\n/help — помощь"


class ImplantBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.IMPLANT, "implant_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("implants", self.cmd_implants))
    
    async def cmd_implants(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🦷 <b>Импланты</b>\n\nТитановые и циркониевые импланты", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🦷 <b>Привет, {name}!</b>\n\nЯ <b>ImplantBot</b>.\n\n/implants — импланты\n/help — помощь"


class InclusiveBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.INCLUSIVE, "inclusive_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("support", self.cmd_support))
    
    async def cmd_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💚 <b>Поддержка</b>\n\nТы не один", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🌈 <b>Привет, {name}!</b>\n\nЯ <b>InclusiveBot</b>.\n\n/support — поддержка\n/help — помощь"


class JokeBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.JOKE, "joke_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("joke", self.cmd_joke))
    
    async def cmd_joke(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        jokes = ["Почему программисты любят осень? Потому что в это время много листьев (листов)"]
        await update.message.reply_text(random.choice(jokes))
    
    def _get_welcome_message(self, name: str) -> str:
        return f"😂 <b>Привет, {name}!</b>\n\nЯ <b>JokeBot</b>.\n\n/joke — шутка\n/help — помощь"


class KartaBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.KARTA, "karta_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("map", self.cmd_map))
    
    async def cmd_map(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🗺️ <b>Карта услуг</b>\n\nСкоро здесь появится список", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🗺️ <b>Привет, {name}!</b>\n\nЯ <b>KartaBot</b>.\n\n/map — карта\n/help — помощь"


class KidBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.KID, "kid_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("game", self.cmd_game))
    
    async def cmd_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        number = random.randint(1, 10)
        context.user_data['game_number'] = number
        await update.message.reply_text(f"🎮 Угадай число! Я загадал число от 1 до 10")
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🧸 <b>Привет, {name}!</b>\n\nЯ <b>KidBot</b>.\n\n/game — игра\n/help — помощь"


class OrthoBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.ORTHO, "ortho_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("braces", self.cmd_braces))
    
    async def cmd_braces(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🦷 <b>Брекеты</b>\n\nМеталлические, керамические, сапфировые", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🦷 <b>Привет, {name}!</b>\n\nЯ <b>OrthoBot</b>.\n\n/braces — брекеты\n/help — помощь"


class PhiloBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.PHILO, "philo_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("quote", self.cmd_quote))
    
    async def cmd_quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        quotes = ["📜 Познай самого себя — Сократ"]
        await update.message.reply_text(random.choice(quotes))
    
    def _get_welcome_message(self, name: str) -> str:
        return f"📜 <b>Привет, {name}!</b>\n\nЯ <b>PhiloBot</b>.\n\n/quote — цитата\n/help — помощь"


class ShopBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.SHOP, "shop_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("catalog", self.cmd_catalog))
    
    async def cmd_catalog(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🛍️ <b>Каталог</b>\n\nСкоро здесь появятся товары!", parse_mode=ParseMode.HTML)
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🛍️ <b>Привет, {name}!</b>\n\nЯ <b>ShopBot</b>.\n\n/catalog — каталог\n/help — помощь"


class AIAgentBot(BaseBot):
    def __init__(self, token: str):
        super().__init__(token, BotPersonality.AI_AGENT, "ai_agent_bot")
    
    def _register_handlers(self, app: Application):
        super()._register_handlers(app)
        app.add_handler(CommandHandler("capabilities", self.cmd_capabilities))
    
    async def cmd_capabilities(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 *AI Agent — возможности*\n\n"
            "• 📝 Обработка текста\n"
            "• 🔍 Анализ данных\n"
            "• 💡 Генерация идей",
            parse_mode='Markdown'
        )
    
    def _get_welcome_message(self, name: str) -> str:
        return f"🤖 *Привет, {name}!*\n\nЯ *AI Agent*.\n\n/capabilities — возможности\n/help — помощь"


# РЕЕСТР БОТОВ
BOT_CLASSES = {
    "admin_bot": AdminBot,
    "ai_agent_bot": AIAgentBot,
    "clean_bot": CleanBot,
    "dentai_bot": DentaiBot,
    "dentai_help_bot": DentaiHelpBot,
    "dream_bot": DreamBot,
    "family_bot": FamilyBot,
    "implant_bot": ImplantBot,
    "inclusive_bot": InclusiveBot,
    "joke_bot": JokeBot,
    "karta_bot": KartaBot,
    "kid_bot": KidBot,
    "ortho_bot": OrthoBot,
    "philo_bot": PhiloBot,
    "prof_bot": ProfBot,
    "shop_bot": ShopBot,
}


def get_token(bot_name: str) -> str:
    """Получение токена из переменных окружения"""
    token_key = f"{bot_name.upper().replace('_BOT', '_BOT_TOKEN')}"
    token = os.getenv(token_key)
    if not token:
        token = os.getenv("MAIN_BOT_TOKEN", "")
    return token


async def run_bot(bot_name: str):
    bot_class = BOT_CLASSES.get(bot_name)
    if not bot_class:
        raise ValueError(f"Unknown bot: {bot_name}")
    token = get_token(bot_name)
    if not token:
        raise ValueError(f"No token for {bot_name}")
    bot = bot_class(token)
    await bot.run()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python all_bots.py <bot_name>")
        sys.exit(1)
    asyncio.run(run_bot(sys.argv[1]))
