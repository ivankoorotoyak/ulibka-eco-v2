#!/usr/bin/env python3
"""
Менеджер состояния экосистемы с поддержкой Lockbox и fallback на .env
Версия: 6.3
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("state_manager")


class StateManager:
    """Менеджер состояния с поддержкой Lockbox"""
    
    def __init__(self, state_file: str = "/opt/smile_bots/ecosystem_state.json"):
        self.state_file = Path(state_file)
        self.state = self._load_state()
        self._lockbox_available = None
        self._env_fallback = {}
    
    def _load_state(self) -> Dict:
        """Загрузка состояния из файла"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        return {}
    
    def _save_state(self):
        """Сохранение состояния в файл"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def _fetch_secrets_from_lockbox(self) -> Dict[str, str]:
        """
        Получение секретов из Lockbox с fallback на .env
        Возвращает словарь с секретами
        """
        secrets = {}
        
        # Попытка получить из Lockbox
        try:
            from lockbox_client import LockboxWrapper
            lockbox = LockboxWrapper(
                folder_id=os.getenv("FOLDER_ID", "b1gjatvnea5nfs88fncv"),
                secret_id=os.getenv("LOCKBOX_SECRET_ID", "e6qra8dstaqig9djfa02")
            )
            secrets = lockbox.get_all()
            if secrets:
                logger.info(f"Secrets loaded from Lockbox: {len(secrets)} keys")
                self._lockbox_available = True
                return secrets
        except ImportError:
            logger.warning("Lockbox client not available, using .env fallback")
        except Exception as e:
            logger.warning(f"Lockbox unavailable: {e}, falling back to .env")
        
        # Fallback на .env файл
        self._lockbox_available = False
        env_file = Path("/opt/smile_bots/.env")
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self._env_fallback[key] = value.strip(' "\'')
                logger.info(f"Secrets loaded from .env: {len(self._env_fallback)} keys")
                return self._env_fallback
            except Exception as e:
                logger.error(f"Failed to read .env: {e}")
        
        logger.warning("No secrets available from Lockbox or .env")
        return {}
    
    def get_secret(self, key: str, default: str = None) -> Optional[str]:
        """
        Получение секрета по ключу с fallback
        """
        # Сначала пробуем Lockbox
        try:
            from lockbox_client import LockboxWrapper
            lockbox = LockboxWrapper(
                folder_id=os.getenv("FOLDER_ID", "b1gjatvnea5nfs88fncv"),
                secret_id=os.getenv("LOCKBOX_SECRET_ID", "e6qra8dstaqig9djfa02")
            )
            value = lockbox.get(key)
            if value:
                return value
        except Exception as e:
            logger.debug(f"Lockbox get failed for {key}: {e}")
        
        # Fallback на .env
        env_file = Path("/opt/smile_bots/.env")
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith(f"{key}="):
                            return line.split('=', 1)[1].strip(' "\'')
            except Exception:
                pass
        
        # Fallback на os.environ
        value = os.getenv(key)
        if value:
            return value
        
        return default
    
    def is_lockbox_available(self) -> bool:
        """Проверка доступности Lockbox"""
        if self._lockbox_available is None:
            self._fetch_secrets_from_lockbox()
        return self._lockbox_available
    
    def update_state(self, updates: Dict):
        """Обновление состояния"""
        self.state.update(updates)
        self.state["last_updated"] = datetime.now().isoformat()
        self._save_state()
    
    def get_bot_status(self, bot_name: str) -> Dict:
        """Получить статус конкретного бота"""
        return self.state.get("bots", {}).get(bot_name, {})
    
    def get_all_bots_status(self) -> Dict:
        """Получить статус всех ботов"""
        return self.state.get("bots", {})
    
    def record_metric(self, metric_name: str, value: Any):
        """Запись метрики"""
        if "metrics" not in self.state:
            self.state["metrics"] = {}
        self.state["metrics"][metric_name] = value
        self._save_state()


if __name__ == "__main__":
    # Тестовый запуск
    manager = StateManager()
    print(f"Lockbox available: {manager.is_lockbox_available()}")
    print(f"State: {json.dumps(manager.state, indent=2, default=str)[:500]}")
