#!/usr/bin/env python3
"""
Быстрый сборщик метрик с кешированием
"""
import os
import json
import time
import psutil
import subprocess
from datetime import datetime
from pathlib import Path

CACHE_FILE = Path("/tmp/ulibka_metrics_cache.json")
CACHE_TTL = 30  # секунд

class FastMetrics:
    def __init__(self):
        self.cache = None
        self.cache_time = 0
    
    def get_system_metrics(self):
        """Быстрый сбор системных метрик"""
        return {
            'cpu': psutil.cpu_percent(interval=0.1),  # Быстрый замер
            'memory': psutil.virtual_memory().percent,
            'memory_used': psutil.virtual_memory().used / (1024**3),  # в GB
            'memory_total': psutil.virtual_memory().total / (1024**3),
            'disk': psutil.disk_usage('/').percent,
            'disk_used': psutil.disk_usage('/').used / (1024**3),
            'disk_total': psutil.disk_usage('/').total / (1024**3),
            'uptime': time.time() - psutil.boot_time()
        }
    
    def get_bot_metrics(self):
        """Быстрый сбор метрик ботов"""
        result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        screen_out = result.stdout
        
        bots = {
            'plus': 'plus_bot',
            'joke': 'joke_bot',
            'clean': 'clean_bot',
            'implant': 'implant_bot',
            'kid': 'kid_bot',
            'philo': 'philo_bot',
            'prof': 'prof_bot',
            'karta': 'karta_bot',
            'dentai': 'dentai_bot',
            'admin': 'admin_bot'
        }
        
        active = []
        for short, full in bots.items():
            if full in screen_out:
                active.append(short)
        
        return {
            'total': len(bots),
            'active': len(active),
            'active_list': active,
            'inactive': [b for b in bots.keys() if b not in active]
        }
    
    def get_redis_metrics(self):
        """Быстрая проверка Redis"""
        try:
            with open('/root/.redis_pass.txt', 'r') as f:
                redis_pass = f.read().strip()
            
            result = subprocess.run(
                ['docker', 'exec', 'redis-ulibka', 'redis-cli', '-a', redis_pass, 'ping'],
                capture_output=True, text=True, timeout=2
            )
            
            if 'PONG' in result.stdout:
                # Получаем дополнительную информацию
                info = subprocess.run(
                    ['docker', 'exec', 'redis-ulibka', 'redis-cli', '-a', redis_pass, 'INFO', 'memory'],
                    capture_output=True, text=True, timeout=2
                )
                used_memory = 0
                for line in info.stdout.split('\n'):
                    if line.startswith('used_memory:'):
                        used_memory = int(line.split(':')[1]) / (1024**2)  # в MB
                        break
                
                return {
                    'status': 'online',
                    'latency': 'fast',
                    'memory_mb': round(used_memory, 1)
                }
        except:
            pass
        
        return {'status': 'offline', 'latency': 'unknown', 'memory_mb': 0}
    
    def get_backup_metrics(self):
        """Информация о бэкапах"""
        backup_dir = Path('/root/backups/db')
        if backup_dir.exists():
            files = list(backup_dir.glob('*.db'))
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                latest_size = latest.stat().st_size / (1024**2)  # в MB
                return {
                    'count': len(files),
                    'latest': latest.name,
                    'latest_size_mb': round(latest_size, 1),
                    'latest_time': datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
                }
        return {'count': 0, 'latest': None}
    
    def get_all_metrics(self):
        """Кешированный сбор всех метрик"""
        now = time.time()
        
        # Проверяем кеш
        if self.cache and (now - self.cache_time) < CACHE_TTL:
            return self.cache
        
        # Собираем свежие метрики
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_metrics(),
            'bots': self.get_bot_metrics(),
            'redis': self.get_redis_metrics(),
            'backups': self.get_backup_metrics()
        }
        
        # Сохраняем в кеш
        self.cache = metrics
        self.cache_time = now
        
        # Сохраняем в файл для истории
        with open(CACHE_FILE, 'w') as f:
            json.dump(metrics, f)
        
        return metrics

# Для быстрого тестирования
if __name__ == "__main__":
    fm = FastMetrics()
    metrics = fm.get_all_metrics()
    print(json.dumps(metrics, indent=2))
