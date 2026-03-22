"""Базовый класс для всех ботов"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional
from telegram.ext import Application

logger = logging.getLogger(__name__)


class BaseBot(ABC):
    """Базовый класс бота с методом run()"""
    
    def __init__(self, token: str):
        self.token = token
        self.application: Optional[Application] = None
    
    @abstractmethod
    async def _register_handlers(self) -> None:
        """Регистрация обработчиков"""
        pass
    
    async def run(self) -> None:
        """Запуск бота с БЛОКИРУЮЩИМ ОЖИДАНИЕМ"""
        self.application = Application.builder().token(self.token).build()
        await self._register_handlers()
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info(f"✅ {self.__class__.__name__} запущен")
        
        # БЛОКИРУЮЩЕЕ ОЖИДАНИЕ (критический фикс)
        await asyncio.Event().wait()
    
    async def stop(self) -> None:
        """Остановка бота"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info(f"🛑 {self.__class__.__name__} остановлен")
