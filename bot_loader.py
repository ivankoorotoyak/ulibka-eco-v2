#!/usr/bin/env python3
"""
bot_loader.py - Универсальный загрузчик ботов
Версия: 3.0 (STRAT-004)
Критический фикс: блокирующий вызов asyncio.run(main())
"""

import os
import sys
import asyncio
import signal
import logging
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/smile_bots/bot_loader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class BotConfig:
    """Конфигурация бота"""
    name: str
    token: str
    class_name: str
    module_path: str
    enabled: bool = True
    retry_count: int = 5
    retry_delay: float = 10.0


class BotLoader:
    """Загрузчик ботов с graceful shutdown"""
    
    def __init__(self):
        self.bots: Dict[str, BotConfig] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self._shutdown_event = asyncio.Event()
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Загрузка конфигурации из .env"""
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        sys.path.insert(0, str(Path(__file__).parent))
        bots_dir = Path(__file__).parent / 'bots'
        
        if not bots_dir.exists():
            logger.warning(f"Директория ботов не найдена: {bots_dir}, создаю")
            bots_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for bot_file in bots_dir.glob("*.py"):
            if bot_file.name.startswith('__'):
                continue
            
            module_name = f"bots.{bot_file.stem}"
            token_key = f"{bot_file.stem.upper()}_TOKEN"
            token = os.getenv(token_key)
            
            if not token:
                logger.warning(f"Токен не найден для {token_key}")
                continue
            
            try:
                module = __import__(module_name, fromlist=[''])
                bot_class = None
                
                for attr_name in dir(module):
                    if attr_name.endswith('Bot') and attr_name != 'BaseBot':
                        bot_class = attr_name
                        break
                
                if not bot_class:
                    logger.warning(f"Класс Bot не найден в {module_name}")
                    continue
                
                self.bots[bot_file.stem] = BotConfig(
                    name=bot_file.stem,
                    token=token,
                    class_name=bot_class,
                    module_path=module_name,
                    enabled=os.getenv(f"{token_key}_ENABLED", "true").lower() == "true"
                )
                
                logger.info(f"✅ Загружен бот: {bot_file.stem} -> {bot_class}")
                
            except Exception as e:
                logger.error(f"Ошибка загрузки {module_name}: {e}")
    
    async def _run_bot_with_retry(self, config: BotConfig) -> None:
        """Запуск бота с retry и блокирующим ожиданием"""
        if not config.enabled:
            logger.info(f"Бот {config.name} отключен")
            return
        
        retries = 0
        
        while retries < config.retry_count and not self._shutdown_event.is_set():
            try:
                module = __import__(config.module_path, fromlist=[config.class_name])
                bot_class = getattr(module, config.class_name)
                bot_instance = bot_class(token=config.token)
                
                logger.info(f"🚀 Запуск бота: {config.name}")
                
                # БЛОКИРУЮЩИЙ ВЫЗОВ через asyncio.Event().wait()
                await bot_instance.run()
                
                retries = 0
                
            except Exception as e:
                retries += 1
                logger.error(f"❌ Ошибка {config.name} ({retries}/{config.retry_count}): {e}")
                
                if retries < config.retry_count and not self._shutdown_event.is_set():
                    delay = config.retry_delay * (2 ** (retries - 1))
                    await asyncio.sleep(delay)
        
        if retries == config.retry_count:
            logger.critical(f"💀 Бот {config.name} остановлен")
    
    async def run_bot(self, bot_name: str) -> None:
        """Запуск конкретного бота"""
        if bot_name not in self.bots:
            logger.error(f"Бот {bot_name} не найден")
            return
        await self._run_bot_with_retry(self.bots[bot_name])
    
    async def run_all(self) -> None:
        """Запуск всех ботов"""
        for name, config in self.bots.items():
            if config.enabled:
                self.tasks[name] = asyncio.create_task(
                    self._run_bot_with_retry(config),
                    name=f"bot_{name}"
                )
        
        if not self.tasks:
            logger.error("Нет активных ботов")
            await self._shutdown_event.wait()
            return
        
        logger.info(f"🎯 Запущено {len(self.tasks)} ботов")
        await asyncio.gather(*self.tasks.values(), return_exceptions=True)
    
    async def graceful_shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("🛑 Остановка ботов...")
        self._shutdown_event.set()
        
        for name, task in self.tasks.items():
            task.cancel()
            logger.info(f"  Отменен: {name}")
        
        if self.tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.tasks.values(), return_exceptions=True),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.warning("⚠️ Таймаут остановки")
        
        logger.info("✅ Боты остановлены")


def setup_signal_handlers(loader: BotLoader) -> None:
    """Настройка обработчиков сигналов"""
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(loader.graceful_shutdown())
        )


def main() -> None:
    """Точка входа с БЛОКИРУЮЩИМ ВЫЗОВОМ asyncio.run()"""
    loader = BotLoader()
    
    if len(sys.argv) > 1:
        bot_name = sys.argv[1]
        logger.info(f"🎯 Запуск бота: {bot_name}")
        
        async def run_single():
            setup_signal_handlers(loader)
            await loader.run_bot(bot_name)
        
        asyncio.run(run_single())
    else:
        logger.info("🎯 Запуск всех ботов")
        
        async def run_all():
            setup_signal_handlers(loader)
            await loader.run_all()
        
        asyncio.run(run_all())


if __name__ == "__main__":
    # КРИТИЧЕСКИЙ ФИКС STRAT-004: БЛОКИРУЮЩИЙ ВЫЗОВ
    main()
