#!/usr/bin/env python3
"""
Модуль сбора метрик для Prometheus
Экспортирует метрики через HTTP endpoint
Версия: 2.0
"""

import os
import time
import logging
import threading
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not installed. Run: pip install prometheus-client")

logger = logging.getLogger("metrics")


class BotMetrics:
    """
    Сбор метрик для ботов
    Использует прометеус-совместимый формат
    """
    
    def __init__(self, registry=None):
        self._lock = threading.Lock()
        self._metrics = defaultdict(lambda: defaultdict(int))
        self._response_times = defaultdict(list)
        self._start_time = time.time()
        
        if PROMETHEUS_AVAILABLE:
            self.registry = registry or REGISTRY
            
            # Prometheus метрики
            self.bot_requests = Counter(
                'smile_bot_requests_total',
                'Total number of bot requests',
                ['bot_name', 'command'],
                registry=self.registry
            )
            self.bot_errors = Counter(
                'smile_bot_errors_total',
                'Total number of bot errors',
                ['bot_name', 'error_type'],
                registry=self.registry
            )
            self.bot_response_time = Histogram(
                'smile_bot_response_time_seconds',
                'Bot response time in seconds',
                ['bot_name', 'command'],
                buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
                registry=self.registry
            )
            self.active_users = Gauge(
                'smile_bot_active_users',
                'Number of active users in last hour',
                ['bot_name'],
                registry=self.registry
            )
            self.bot_uptime = Gauge(
                'smile_bot_uptime_seconds',
                'Bot uptime in seconds',
                ['bot_name'],
                registry=self.registry
            )
            self.message_queue_size = Gauge(
                'smile_bot_message_queue_size',
                'Current message queue size',
                ['bot_name'],
                registry=self.registry
            )
            self.db_connections = Gauge(
                'smile_bot_db_connections',
                'Database connection pool size',
                ['database'],
                registry=self.registry
            )
            self.redis_connections = Gauge(
                'smile_bot_redis_connections',
                'Redis connection pool size',
                registry=self.registry
            )
    
    def record_request(self, bot_name: str, command: str):
        """Запись запроса к боту"""
        with self._lock:
            self._metrics[bot_name][f"requests_{command}"] += 1
        
        if PROMETHEUS_AVAILABLE:
            self.bot_requests.labels(bot_name=bot_name, command=command).inc()
    
    def record_error(self, bot_name: str, error_type: str):
        """Запись ошибки"""
        with self._lock:
            self._metrics[bot_name][f"errors_{error_type}"] += 1
        
        if PROMETHEUS_AVAILABLE:
            self.bot_errors.labels(bot_name=bot_name, error_type=error_type).inc()
    
    def record_response_time(self, bot_name: str, command: str, duration: float):
        """Запись времени ответа"""
        with self._lock:
            self._response_times[bot_name].append(duration)
            if len(self._response_times[bot_name]) > 1000:
                self._response_times[bot_name] = self._response_times[bot_name][-1000:]
        
        if PROMETHEUS_AVAILABLE:
            self.bot_response_time.labels(bot_name=bot_name, command=command).observe(duration)
    
    def update_active_users(self, bot_name: str, count: int):
        """Обновление количества активных пользователей"""
        if PROMETHEUS_AVAILABLE:
            self.active_users.labels(bot_name=bot_name).set(count)
    
    def update_uptime(self, bot_name: str, start_time: float = None):
        """Обновление времени работы"""
        if start_time is None:
            start_time = self._start_time
        uptime = time.time() - start_time
        if PROMETHEUS_AVAILABLE:
            self.bot_uptime.labels(bot_name=bot_name).set(uptime)
        return uptime
    
    def update_queue_size(self, bot_name: str, size: int):
        """Обновление размера очереди сообщений"""
        if PROMETHEUS_AVAILABLE:
            self.message_queue_size.labels(bot_name=bot_name).set(size)
    
    def update_db_connections(self, database: str, count: int):
        """Обновление количества соединений с БД"""
        if PROMETHEUS_AVAILABLE:
            self.db_connections.labels(database=database).set(count)
    
    def update_redis_connections(self, count: int):
        """Обновление количества соединений с Redis"""
        if PROMETHEUS_AVAILABLE:
            self.redis_connections.set(count)
    
    def get_metrics_dict(self) -> Dict:
        """Получение метрик в виде словаря (для отладки)"""
        with self._lock:
            avg_response_times = {}
            for bot, times in self._response_times.items():
                avg_response_times[bot] = {
                    "avg": sum(times) / len(times) if times else 0,
                    "count": len(times),
                    "min": min(times) if times else 0,
                    "max": max(times) if times else 0
                }
            
            return {
                "uptime": time.time() - self._start_time,
                "requests": dict(self._metrics),
                "response_times": avg_response_times,
                "prometheus_available": PROMETHEUS_AVAILABLE
            }
    
    def get_prometheus_metrics(self) -> str:
        """Получение метрик в формате Prometheus"""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus client not available\n"
        return generate_latest(self.registry).decode('utf-8')
    
    def reset_metrics(self):
        """Сброс всех метрик"""
        with self._lock:
            self._metrics.clear()
            self._response_times.clear()
        logger.info("Metrics reset")


# Глобальный экземпляр
_metrics = BotMetrics()


def get_metrics() -> BotMetrics:
    """Получение глобального экземпляра метрик"""
    return _metrics


def record_request(bot_name: str, command: str):
    """Утилитарная функция для записи запроса"""
    _metrics.record_request(bot_name, command)


def record_error(bot_name: str, error_type: str):
    """Утилитарная функция для записи ошибки"""
    _metrics.record_error(bot_name, error_type)


def record_response_time(bot_name: str, command: str, duration: float):
    """Утилитарная функция для записи времени ответа"""
    _metrics.record_response_time(bot_name, command, duration)


def get_metrics_handler():
    """Обработчик для HTTP endpoint"""
    from flask import Response
    return Response(_metrics.get_prometheus_metrics(), mimetype=CONTENT_TYPE_LATEST if PROMETHEUS_AVAILABLE else "text/plain")


if __name__ == "__main__":
    # Тестовый запуск
    print("=== Bot Metrics Module ===")
    print(f"Prometheus available: {PROMETHEUS_AVAILABLE}")
    print("\nTest metrics:")
    _metrics.record_request("test_bot", "/start")
    _metrics.record_response_time("test_bot", "/start", 0.123)
    print(_metrics.get_metrics_dict())
    if PROMETHEUS_AVAILABLE:
        print("\nPrometheus output (first 500 chars):")
        print(_metrics.get_prometheus_metrics()[:500])
