#!/usr/bin/env python3
"""
Сборщик метрик для системы мониторинга
"""
import os
import json
import time
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

class MetricsCollector:
    def __init__(self):
        self.data_dir = Path("/root/ulibka_eco_v2/data/status")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def collect_system_metrics(self):
        """Сбор системных метрик"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'load': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
        }
        return metrics
    
    def collect_bot_metrics(self):
        """Сбор метрик ботов"""
        result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        screen_output = result.stdout
        
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
        
        status = {}
        for short, full in bots.items():
            status[short] = full in screen_output
        
        return {
            'total': len(bots),
            'active': sum(status.values()),
            'details': status
        }
    
    def collect_redis_metrics(self):
        """Сбор метрик Redis"""
        try:
            with open('/root/.redis_pass.txt', 'r') as f:
                redis_pass = f.read().strip()
            
            result = subprocess.run(
                ['docker', 'exec', 'redis-ulibka', 'redis-cli', '-a', redis_pass, 'INFO'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                return {'status': 'online', 'details': 'Redis OK'}
        except:
            pass
        return {'status': 'offline', 'details': 'Redis недоступен'}
    
    def collect_all(self):
        """Сбор всех метрик"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': self.collect_system_metrics(),
            'bots': self.collect_bot_metrics(),
            'redis': self.collect_redis_metrics()
        }
    
    def save_metrics(self):
        """Сохранение метрик в файл"""
        metrics = self.collect_all()
        filename = self.data_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Сохраняем последние метрики для быстрого доступа
        with open(self.data_dir / 'latest.json', 'w') as f:
            json.dump(metrics, f)
        
        return metrics

if __name__ == "__main__":
    collector = MetricsCollector()
    metrics = collector.save_metrics()
    print(f"✅ Метрики сохранены: {metrics['bots']['active']}/10 ботов работают")
