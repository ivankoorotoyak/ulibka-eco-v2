#!/usr/bin/env python3
"""
Pytest конфигурация и фикстуры для тестирования ботов
"""

import os
import sys
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Добавляем путь к модулям
sys.path.insert(0, '/opt/smile_bots')

from generic_bot import BaseBot
from state_manager import StateManager
from log_aggregator import LogAggregator


@pytest.fixture
def temp_env_file():
    """Временный .env файл для тестов"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("TEST_TOKEN=123456:ABCdef\n")
        f.write("TEST_API_KEY=test_key\n")
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_log_dir():
    """Временная директория для логов"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "test.log"
        yield tmpdir


@pytest.fixture
def mock_bot():
    """Mock бота для тестирования"""
    class TestBot(BaseBot):
        def __init__(self, token="test_token"):
            super().__init__(token, "test_bot")
    
    bot = TestBot("test_token")
    return bot


@pytest.fixture
def mock_state_manager(temp_env_file):
    """StateManager с временными файлами"""
    with patch.dict(os.environ, {"TEST_MODE": "1"}):
        manager = StateManager(
            state_file=tempfile.NamedTemporaryFile(suffix='.json').name
        )
        yield manager


@pytest.fixture
def mock_telegram_update():
    """Mock Telegram Update объекта"""
    update = AsyncMock()
    update.effective_user = AsyncMock()
    update.effective_user.id = 123456
    update.effective_user.first_name = "TestUser"
    update.effective_user.username = "testuser"
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()
    update.message.chat_id = 123456
    return update


@pytest.fixture
def mock_telegram_context():
    """Mock Telegram Context"""
    context = AsyncMock()
    context.bot = AsyncMock()
    context.bot.send_message = AsyncMock()
    context.user_data = {}
    context.chat_data = {}
    return context


@pytest.fixture
def sample_logs():
    """Пример логов для тестирования агрегатора"""
    return [
        "2026-03-21 10:00:00 - prof_bot - INFO - Bot started",
        "2026-03-21 10:01:00 - prof_bot - ERROR - Connection failed",
        "2026-03-21 10:02:00 - dentai_bot - INFO - New user",
        "2026-03-21 10:03:00 - dentai_bot - WARNING - Slow response",
        "2026-03-21 10:04:00 - prof_bot - INFO - Command received",
    ]


@pytest.fixture
def sample_state():
    """Пример состояния для тестов"""
    return {
        "version": "6.3",
        "last_updated": "2026-03-21T12:00:00",
        "ecosystem": {
            "name": "Улыбка",
            "total_bots": 15,
            "active_bots": 15,
            "server": "5.42.106.10"
        },
        "bots": {},
        "metrics": {
            "total_elements": 6500,
            "categories": 20
        }
    }
