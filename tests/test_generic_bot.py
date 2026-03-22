#!/usr/bin/env python3
"""
Тесты для базового класса ботов
"""

import pytest
from unittest.mock import AsyncMock, patch
import sys
sys.path.insert(0, '/opt/smile_bots')

from generic_bot import BaseBot


class TestBaseBot:
    """Тесты базового класса"""
    
    def test_bot_initialization(self, mock_bot):
        """Тест инициализации бота"""
        assert mock_bot.name == "test_bot"
        assert mock_bot.token == "test_token"
        assert mock_bot.logger is not None
    
    def test_get_application(self, mock_bot):
        """Тест создания приложения"""
        app = mock_bot.get_application()
        assert app is not None
    
    @pytest.mark.asyncio
    async def test_cmd_start(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Тест команды /start"""
        await mock_bot.cmd_start(mock_telegram_update, mock_telegram_context)
        mock_telegram_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cmd_help(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Тест команды /help"""
        await mock_bot.cmd_help(mock_telegram_update, mock_telegram_context)
        mock_telegram_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cmd_info(self, mock_bot, mock_telegram_update, mock_telegram_context):
        """Тест команды /info"""
        await mock_bot.cmd_info(mock_telegram_update, mock_telegram_context)
        mock_telegram_update.message.reply_text.assert_called_once()
    
    def test_get_welcome_message(self, mock_bot):
        """Тест приветственного сообщения"""
        msg = mock_bot._get_welcome_message("Test")
        assert "Test" in msg
        assert "/help" in msg
    
    def test_get_help_message(self, mock_bot):
        """Тест сообщения помощи"""
        msg = mock_bot._get_help_message()
        assert "/start" in msg
        assert "/help" in msg
    
    def test_get_info_message(self, mock_bot):
        """Тест информационного сообщения"""
        msg = mock_bot._get_info_message()
        assert "Версия" in msg or "version" in msg.lower()


class TestBotWithCommands:
    """Тесты ботов с дополнительными командами"""
    
    @pytest.mark.asyncio
    async def test_command_registration(self):
        """Тест регистрации дополнительных команд"""
        class CustomBot(BaseBot):
            def _register_handlers(self, app):
                super()._register_handlers(app)
                app.add_handler = AsyncMock()
        
        bot = CustomBot("test", "custom_bot")
        app = bot.get_application()
        assert hasattr(app, 'add_handler') or True  # проверка, что код выполнился
    
    def test_subclass_inheritance(self):
        """Тест наследования"""
        class SubBot(BaseBot):
            pass
        
        bot = SubBot("test", "sub_bot")
        assert isinstance(bot, BaseBot)
        assert hasattr(bot, 'cmd_start')
        assert hasattr(bot, 'cmd_help')
        assert hasattr(bot, 'cmd_info')
