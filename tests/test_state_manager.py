#!/usr/bin/env python3
"""
Тесты для менеджера состояния
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '/opt/smile_bots')

from state_manager import StateManager


class TestStateManager:
    """Тесты StateManager"""
    
    def test_init(self, mock_state_manager):
        """Тест инициализации"""
        assert mock_state_manager is not None
    
    def test_load_state_empty(self, temp_env_file):
        """Тест загрузки пустого состояния"""
        with tempfile.NamedTemporaryFile(suffix='.json') as f:
            manager = StateManager(state_file=f.name)
            state = manager.load_state()
            assert state == {}
    
    def test_save_state(self, temp_env_file):
        """Тест сохранения состояния"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            state_file = f.name
        
        try:
            manager = StateManager(state_file=state_file)
            test_state = {"test": "value", "timestamp": "2026-03-21"}
            manager.save_state(test_state)
            
            with open(state_file, 'r') as f:
                loaded = json.load(f)
            assert loaded == test_state
        finally:
            os.unlink(state_file)
    
    def test_update_state(self, mock_state_manager):
        """Тест обновления состояния"""
        initial = {"version": "1.0"}
        mock_state_manager.state = initial
        
        updates = {"metrics": {"test": 123}}
        mock_state_manager.update_state(updates)
        
        assert "version" in mock_state_manager.state
        assert mock_state_manager.state["metrics"]["test"] == 123
    
    @patch('state_manager.LockboxWrapper')
    def test_fetch_secrets_success(self, mock_lockbox, temp_env_file):
        """Тест успешного получения секретов из Lockbox"""
        mock_lockbox.return_value.get_all.return_value = {"TOKEN": "test123"}
        
        with tempfile.NamedTemporaryFile(suffix='.json') as f:
            manager = StateManager(state_file=f.name)
            secrets = manager._fetch_secrets_from_lockbox()
            assert secrets == {"TOKEN": "test123"}
    
    @patch('state_manager.LockboxWrapper')
    def test_fetch_secrets_fallback_to_env(self, mock_lockbox, temp_env_file):
        """Тест fallback на .env при недоступности Lockbox"""
        mock_lockbox.side_effect = Exception("Lockbox unavailable")
        
        with patch.dict(os.environ, {"TEST_SECRET": "env_value"}):
            with tempfile.NamedTemporaryFile(suffix='.json') as f:
                manager = StateManager(state_file=f.name)
                secrets = manager._fetch_secrets_from_lockbox()
                # Должен вернуть пустой словарь (нет ошибки)
                assert isinstance(secrets, dict)
    
    def test_get_bot_status(self, mock_state_manager):
        """Тест получения статуса бота"""
        mock_state_manager.state = {
            "bots": {
                "test_bot": {"status": "active", "uptime": 3600}
            }
        }
        status = mock_state_manager.get_bot_status("test_bot")
        assert status["status"] == "active"
    
    def test_get_all_bots_status(self, mock_state_manager):
        """Тест получения статуса всех ботов"""
        mock_state_manager.state = {
            "bots": {
                "bot1": {"status": "active"},
                "bot2": {"status": "inactive"}
            }
        }
        all_status = mock_state_manager.get_all_bots_status()
        assert len(all_status) == 2
        assert all_status["bot1"]["status"] == "active"
    
    def test_record_metric(self, mock_state_manager):
        """Тест записи метрики"""
        mock_state_manager.record_metric("test_metric", 100)
        assert "test_metric" in mock_state_manager.state.get("metrics", {})
    
    @patch('state_manager.logging')
    def test_error_logging_on_lockbox_failure(self, mock_logging, temp_env_file):
        """Тест логирования ошибок Lockbox"""
        with patch('state_manager.LockboxWrapper') as mock_lockbox:
            mock_lockbox.side_effect = Exception("Connection refused")
            
            with tempfile.NamedTemporaryFile(suffix='.json') as f:
                manager = StateManager(state_file=f.name)
                # Не должно быть исключения
                assert manager is not None
                mock_logging.warning.assert_called()
