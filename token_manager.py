#!/usr/bin/env python3
"""
Централизованный менеджер токенов для экосистемы Улыбка
"""

import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TokenManager:
    """Менеджер токенов с поддержкой Lockbox и .env"""
    
    def __init__(self, env_path: str = "/opt/smile_bots/.env"):
        self.env_path = Path(env_path)
        self._loaded = False
        self._load_env()
    
    def _load_env(self):
        """Загрузка переменных из .env файла"""
        if self.env_path.exists():
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value.strip(' "\'')
            self._loaded = True
            logger.debug(f"Loaded env from {self.env_path}")
    
    def get_token(self, bot_name: str) -> Optional[str]:
        """Получение токена для бота"""
        base_name = bot_name.replace('_bot', '').upper()
        
        candidates = [
            f"{base_name}_BOT_TOKEN",
            f"{base_name}_TOKEN",
            bot_name.upper().replace('_BOT', '_BOT_TOKEN'),
        ]
        
        special = {
            "ai_agent_bot": ["AI_AGENT_BOT_TOKEN", "AI_AGENT_TOKEN"],
            "dentai_bot": ["DENTAI_BOT_TOKEN", "DENTAI_TOKEN"],
            "gum_bot": ["GUM_BOT_TOKEN", "GUM_TOKEN"],
            "shop_bot": ["SHOP_BOT_TOKEN", "SHOP_TOKEN"],
        }
        
        if bot_name in special:
            candidates = special[bot_name] + candidates
        
        for key in candidates:
            token = os.getenv(key)
            if token:
                logger.debug(f"Token found for {bot_name} via {key}")
                return token
        
        logger.warning(f"Token not found for {bot_name}")
        return None


token_manager = TokenManager()


def get_token(bot_name: str) -> Optional[str]:
    """Утилитарная функция для получения токена"""
    return token_manager.get_token(bot_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== TOKEN MANAGER TEST ===")
    for bot in ["ai_agent_bot", "dentai_bot", "gum_bot", "shop_bot", "admin_bot"]:
        token = get_token(bot)
        if token:
            print(f"✅ {bot}: {token[:10]}...{token[-3:]}")
        else:
            print(f"❌ {bot}: NOT FOUND")
