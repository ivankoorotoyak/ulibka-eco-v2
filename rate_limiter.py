#!/usr/bin/env python3
"""
Модуль ограничения частоты запросов (Rate Limiting)
Реализует декоратор @rate_limit для защиты от спама
"""

import time
import logging
import functools
from collections import defaultdict
from typing import Dict, Callable, Any
from datetime import datetime, timedelta

logger = logging.getLogger("rate_limiter")


class RateLimiter:
    """
    Ограничитель частоты запросов
    Использует sliding window для отслеживания
    """
    
    def __init__(self):
        self._user_requests: Dict[int, list] = defaultdict(list)
    
    def is_allowed(self, user_id: int, max_calls: int = 30, time_window: int = 60) -> bool:
        """
        Проверка, может ли пользователь выполнить запрос
        
        Args:
            user_id: ID пользователя Telegram
            max_calls: максимальное количество вызовов за окно
            time_window: временное окно в секундах
            
        Returns:
            True если запрос разрешён, False если превышен лимит
        """
        now = time.time()
        window_start = now - time_window
        
        # Очищаем старые записи
        self._user_requests[user_id] = [
            t for t in self._user_requests[user_id] if t > window_start
        ]
        
        # Проверяем лимит
        if len(self._user_requests[user_id]) >= max_calls:
            logger.warning(f"Rate limit exceeded for user {user_id}: "
                          f"{len(self._user_requests[user_id])}/{max_calls} in {time_window}s")
            return False
        
        # Добавляем текущий запрос
        self._user_requests[user_id].append(now)
        return True
    
    def get_remaining(self, user_id: int, max_calls: int = 30, time_window: int = 60) -> int:
        """Получить количество оставшихся запросов"""
        now = time.time()
        window_start = now - time_window
        
        # Очищаем старые записи
        self._user_requests[user_id] = [
            t for t in self._user_requests[user_id] if t > window_start
        ]
        
        used = len(self._user_requests[user_id])
        return max(0, max_calls - used)
    
    def reset(self, user_id: int):
        """Сбросить лимиты для пользователя"""
        if user_id in self._user_requests:
            del self._user_requests[user_id]
            logger.info(f"Rate limit reset for user {user_id}")


# Глобальный экземпляр
_limiter = RateLimiter()


def rate_limit(max_calls: int = 30, time_window: int = 60, cooldown_message: str = None):
    """
    Декоратор для ограничения частоты запросов
    
    Args:
        max_calls: максимальное количество вызовов за окно
        time_window: временное окно в секундах
        cooldown_message: сообщение при превышении лимита
        
    Usage:
        @rate_limit(max_calls=5, time_window=60)
        async def some_handler(update, context):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_id = None
            if hasattr(update, 'effective_user') and update.effective_user:
                user_id = update.effective_user.id
            elif hasattr(update, 'callback_query') and update.callback_query:
                user_id = update.callback_query.from_user.id
            
            if user_id is None:
                # Не удалось определить пользователя, пропускаем
                return await func(update, context, *args, **kwargs)
            
            if not _limiter.is_allowed(user_id, max_calls, time_window):
                remaining = _limiter.get_remaining(user_id, max_calls, time_window)
                msg = cooldown_message or f"⏳ Слишком много запросов. Подождите {remaining} секунд."
                
                if hasattr(update, 'message') and update.message:
                    await update.message.reply_text(msg)
                elif hasattr(update, 'callback_query') and update.callback_query:
                    await update.callback_query.answer(msg, show_alert=True)
                
                logger.info(f"Rate limit blocked user {user_id}")
                return
            
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    return decorator


class PerBotRateLimiter:
    """
    Ограничитель с разными лимитами для разных ботов
    """
    
    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}
    
    def get_limiter(self, bot_name: str) -> RateLimiter:
        if bot_name not in self._limiters:
            self._limiters[bot_name] = RateLimiter()
        return self._limiters[bot_name]
    
    def rate_limit_for_bot(self, bot_name: str, max_calls: int = 30, time_window: int = 60):
        """Декоратор с лимитами для конкретного бота"""
        limiter = self.get_limiter(bot_name)
        
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(update, context, *args, **kwargs):
                user_id = None
                if update.effective_user:
                    user_id = update.effective_user.id
                
                if user_id and not limiter.is_allowed(user_id, max_calls, time_window):
                    if update.message:
                        await update.message.reply_text(
                            f"⏳ Бот {bot_name} временно недоступен. Попробуйте позже."
                        )
                    return
                
                return await func(update, context, *args, **kwargs)
            
            return wrapper
        return decorator


# Экспорт
__all__ = ['rate_limit', 'RateLimiter', 'PerBotRateLimiter']
