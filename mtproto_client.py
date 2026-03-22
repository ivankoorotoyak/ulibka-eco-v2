#!/usr/bin/env python3
"""
MTProto клиент для Telegram API
Используется для функций, недоступных через Bot API
Версия: 1.0
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError, FloodWaitError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("Telethon not installed. Run: pip install telethon")

logger = logging.getLogger("mtproto_client")


class MTProtoClient:
    """Клиент для работы с MTProto API Telegram"""
    
    def __init__(self, session_name: str = "mtproto_session"):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.session_name = session_name
        self.session_path = Path(f"/opt/smile_bots/sessions/{session_name}")
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        self.client: Optional[TelegramClient] = None
        self._connected = False
        
    def is_configured(self) -> bool:
        """Проверка наличия API ключей"""
        if not TELEGRAM_AVAILABLE:
            return False
        return bool(self.api_id and self.api_hash)
    
    async def connect(self) -> bool:
        """Подключение к Telegram"""
        if not self.is_configured():
            logger.warning("MTProto не настроен: отсутствуют TELEGRAM_API_ID или TELEGRAM_API_HASH")
            return False
        
        try:
            self.client = TelegramClient(
                str(self.session_path),
                int(self.api_id),
                self.api_hash
            )
            await self.client.start()
            self._connected = True
            logger.info("✅ MTProto клиент подключён")
            return True
        except FloodWaitError as e:
            logger.error(f"Flood wait: {e.seconds} seconds")
            return False
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            return False
    
    async def disconnect(self):
        """Отключение"""
        if self.client and self._connected:
            await self.client.disconnect()
            self._connected = False
            logger.info("MTProto клиент отключён")
    
    async def ensure_connected(self) -> bool:
        """Убедиться, что клиент подключён"""
        if not self._connected or not self.client:
            return await self.connect()
        return True
    
    async def get_user_info(self, username: str) -> Optional[Dict]:
        """Получить информацию о пользователе по username"""
        if not await self.ensure_connected():
            return None
        
        try:
            user = await self.client.get_entity(username)
            return {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": getattr(user, 'phone', None),
                "is_bot": user.bot if hasattr(user, 'bot') else False
            }
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {username}: {e}")
            return None
    
    async def get_chat_messages(self, chat_id, limit: int = 100) -> List[Dict]:
        """Получить последние сообщения из чата"""
        if not await self.ensure_connected():
            return []
        
        try:
            messages = []
            async for message in self.client.iter_messages(chat_id, limit=limit):
                messages.append({
                    "id": message.id,
                    "text": message.text[:500] if message.text else None,
                    "date": message.date.isoformat(),
                    "sender_id": message.sender_id,
                    "sender_name": getattr(message.sender, 'username', None) if message.sender else None
                })
            return messages
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {e}")
            return []
    
    async def send_message(self, chat_id, text: str) -> Optional[int]:
        """Отправить сообщение от имени пользователя (требуется авторизация)"""
        if not await self.ensure_connected():
            return None
        
        try:
            result = await self.client.send_message(chat_id, text)
            logger.info(f"Сообщение отправлено в {chat_id}")
            return result.id
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return None
    
    async def get_chat_info(self, chat_id) -> Optional[Dict]:
        """Получить информацию о чате/канале"""
        if not await self.ensure_connected():
            return None
        
        try:
            chat = await self.client.get_entity(chat_id)
            return {
                "id": chat.id,
                "title": getattr(chat, 'title', None),
                "username": getattr(chat, 'username', None),
                "participants_count": getattr(chat, 'participants_count', None),
                "is_channel": getattr(chat, 'broadcast', False),
                "is_group": getattr(chat, 'megagroup', False)
            }
        except Exception as e:
            logger.error(f"Ошибка получения чата {chat_id}: {e}")
            return None
    
    async def get_dialogs(self, limit: int = 50) -> List[Dict]:
        """Получить список диалогов"""
        if not await self.ensure_connected():
            return []
        
        try:
            dialogs = []
            async for dialog in self.client.iter_dialogs(limit=limit):
                dialogs.append({
                    "id": dialog.id,
                    "name": dialog.name,
                    "unread_count": dialog.unread_count,
                    "is_user": dialog.is_user,
                    "is_group": dialog.is_group,
                    "is_channel": dialog.is_channel
                })
            return dialogs
        except Exception as e:
            logger.error(f"Ошибка получения диалогов: {e}")
            return []


# Глобальный экземпляр
mtproto = MTProtoClient()


async def test_connection():
    """Тестовая функция для проверки подключения"""
    if await mtproto.connect():
        print("✅ MTProto подключён")
        dialogs = await mtproto.get_dialogs(limit=5)
        print(f"📋 Последние диалоги: {len(dialogs)}")
        await mtproto.disconnect()
        return True
    else:
        print("❌ MTProto не подключён")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connection())
