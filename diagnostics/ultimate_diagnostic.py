#!/usr/bin/env python3
"""
Ультимативная диагностика всех ресурсов
"""
import os
import sys
import time
import json
import psutil
import subprocess
from datetime import datetime
from pathlib import Path

class UltimateDiagnostic:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'bots': {},
            'database': {},
            'redis': {},
            'network': {},
            'optimizations': []
        }
    
    def diagnose_system(self):
        """Полная диагностика системы"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=2, percpu=True)
        cpu_avg = sum(cpu_percent) / len(cpu_percent)
        
        # Память
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Диск
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Процессы
        processes = len(psutil.pids())
        
        self.results['system'] = {
            'cpu': {
                'per_core': [round(c, 1) for c in cpu_percent],
                'average': round(cpu_avg, 1),
                'processes': processes,
                'bottleneck': cpu_avg > 70
            },
            'memory': {
                'total_gb': round(mem.total / (1024**3), 2),
                'used_gb': round(mem.used / (1024**3), 2),
                'percent': mem.percent,
                'swap_gb': round(swap.used / (1024**3), 2),
                'swap_percent': swap.percent,
                'bottleneck': mem.percent > 80 or swap.percent > 10
            },
            'disk': {
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'percent': disk.percent,
                'read_mb': round(disk_io.read_bytes / (1024**2), 1) if disk_io else 0,
                'write_mb': round(disk_io.write_bytes / (1024**2), 1) if disk_io else 0,
                'bottleneck': disk.percent > 85
            }
        }
        
        return self.results['system']
    
    def diagnose_bots(self):
        """Диагностика ботов"""
        result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        screen_out = result.stdout
        
        bots = ['plus', 'joke', 'clean', 'implant', 'kid', 'philo', 'prof', 'karta', 'dentai', 'admin']
        active = []
        
        for bot in bots:
            if f"{bot}_bot" in screen_out:
                active.append(bot)
        
        # Проверяем дублирование
        duplicates = {}
        for bot in bots:
            count = screen_out.count(f"{bot}_bot")
            if count > 1:
                duplicates[bot] = count
        
        # Проверяем потребление памяти каждым ботом
        bot_memory = {}
        for bot in bots:
            result = subprocess.run(
                ['ps', 'aux', '|', 'grep', f'{bot}_bot', '|', 'grep', '-v', 'grep'],
                capture_output=True, text=True, shell=True
            )
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:
                try:
                    parts = lines[0].split()
                    if len(parts) > 5:
                        mem = float(parts[5]) if parts[5].replace('.', '').isdigit() else 0
                        bot_memory[bot] = mem
                except:
                    pass
        
        self.results['bots'] = {
            'total': len(bots),
            'active': len(active),
            'active_list': active,
            'inactive': [b for b in bots if b not in active],
            'duplicates': duplicates,
            'memory_mb': bot_memory,
            'bottleneck': len(active) < len(bots) or len(duplicates) > 0
        }
        
        return self.results['bots']
    
    def diagnose_redis(self):
        """Диагностика Redis"""
        try:
            with open('/root/.redis_pass.txt', 'r') as f:
                redis_pass = f.read().strip()
            
            # Пинг
            ping = subprocess.run(
                ['docker', 'exec', 'redis-ulibka', 'redis-cli', '-a', redis_pass, 'ping'],
                capture_output=True, text=True, timeout=2
            )
            
            if 'PONG' in ping.stdout:
                # Информация
                info = subprocess.run(
                    ['docker', 'exec', 'redis-ulibka', 'redis-cli', '-a', redis_pass, 'INFO'],
                    capture_output=True, text=True, timeout=2
                )
                
                used_memory = 0
                connected_clients = 0
                uptime = 0
                
                for line in info.stdout.split('\n'):
                    if line.startswith('used_memory:'):
                        used_memory = int(line.split(':')[1]) / (1024**2)
                    elif line.startswith('connected_clients:'):
                        connected_clients = int(line.split(':')[1])
                    elif line.startswith('uptime_in_seconds:'):
                        uptime = int(line.split(':')[1])
                
                self.results['redis'] = {
                    'status': 'online',
                    'memory_mb': round(used_memory, 1),
                    'clients': connected_clients,
                    'uptime_hours': round(uptime / 3600, 1),
                    'bottleneck': used_memory > 500 or connected_clients > 50
                }
            else:
                self.results['redis'] = {'status': 'offline', 'bottleneck': True}
        except:
            self.results['redis'] = {'status': 'error', 'bottleneck': True}
        
        return self.results['redis']
    
    def diagnose_database(self):
        """Диагностика SQLite"""
        db_path = Path('/var/lib/ulibka/ulibka.db')
        if db_path.exists():
            size = db_path.stat().st_size / 1024
            
            # Проверка индексов
            indexes = subprocess.run(
                ['sqlite3', str(db_path), "SELECT name FROM sqlite_master WHERE type='index';"],
                capture_output=True, text=True
            )
            
            # Проверка целостности
            integrity = subprocess.run(
                ['sqlite3', str(db_path), 'PRAGMA integrity_check;'],
                capture_output=True, text=True
            )
            
            self.results['database'] = {
                'size_kb': round(size, 1),
                'size_mb': round(size / 1024, 2),
                'indexes': len(indexes.stdout.strip().split('\n')) if indexes.stdout.strip() else 0,
                'integrity': 'ok' if 'ok' in integrity.stdout else 'error',
                'bottleneck': size > 100 * 1024 or 'ok' not in integrity.stdout
            }
        else:
            self.results['database'] = {'status': 'not found', 'bottleneck': True}
        
        return self.results['database']
    
    def diagnose_network(self):
        """Диагностика сети"""
        # Пинг до Telegram
        ping_tg = subprocess.run(
            ['ping', '-c', '2', '-W', '1', 'api.telegram.org'],
            capture_output=True, text=True
        )
        
        # Извлекаем средний пинг
        ping_ms = 0
        for line in ping_tg.stdout.split('\n'):
            if 'avg' in line:
                try:
                    ping_ms = float(line.split('/')[4])
                except:
                    pass
        
        # Проверка открытых портов
        ports = [22, 80, 443, 3000, 9090, 9100, 9101, 6379]
        open_ports = []
        
        for port in ports:
            result = subprocess.run(
                ['ss', '-tlnp', '|', 'grep', f':{port}'],
                capture_output=True, text=True, shell=True
            )
            if result.stdout:
                open_ports.append(port)
        
        self.results['network'] = {
            'ping_telegram_ms': round(ping_ms, 1),
            'open_ports': open_ports,
            'bottleneck': ping_ms > 200
        }
        
        return self.results['network']
    
    def run_all(self):
        """Запуск всех диагностик"""
        print("🔍 Запуск ультимативной диагностики...")
        
        self.diagnose_system()
        self.diagnose_bots()
        self.diagnose_redis()
        self.diagnose_database()
        self.diagnose_network()
        
        # Формируем рекомендации
        if self.results['system']['cpu']['bottleneck']:
            self.results['optimizations'].append("⚡ Высокая нагрузка CPU - добавить workers")
        if self.results['system']['memory']['bottleneck']:
            self.results['optimizations'].append("🧠 Мало памяти - увеличить RAM или оптимизировать")
        if self.results['system']['disk']['bottleneck']:
            self.results['optimizations'].append("💾 Диск почти полный - очистка логов")
        if self.results['bots']['bottleneck']:
            if len(self.results['bots']['inactive']) > 0:
                self.results['optimizations'].append(f"🤖 Не все боты работают: {self.results['bots']['inactive']}")
            if self.results['bots'].get('duplicates'):
                self.results['optimizations'].append(f"🔄 Есть дубликаты ботов: {self.results['bots']['duplicates']}")
        if self.results['redis']['bottleneck']:
            self.results['optimizations'].append("🔴 Redis перегружен - увеличить память")
        if self.results['database']['bottleneck']:
            self.results['optimizations'].append("🗄️ База данных требует оптимизации")
        if self.results['network']['bottleneck']:
            self.results['optimizations'].append("🌐 Высокий пинг - проверить сеть")
        
        # Сохраняем
        with open('diagnostics/ultimate_latest.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Вывод
        print("\n📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ")
        print("=" * 60)
        print(f"CPU: {self.results['system']['cpu']['average']}% (процессов: {self.results['system']['cpu']['processes']})")
        print(f"RAM: {self.results['system']['memory']['percent']}% ({self.results['system']['memory']['used_gb']}/{self.results['system']['memory']['total_gb']} GB)")
        print(f"Диск: {self.results['system']['disk']['percent']}% ({self.results['system']['disk']['used_gb']}/{self.results['system']['disk']['total_gb']} GB)")
        print(f"Боты: {self.results['bots']['active']}/{self.results['bots']['total']} активны")
        if self.results['bots'].get('duplicates'):
            print(f"Дубликаты: {self.results['bots']['duplicates']}")
        print(f"Redis: {self.results['redis']['memory_mb']} MB, {self.results['redis']['clients']} клиентов")
        print(f"База данных: {self.results['database']['size_mb']} MB, индексов: {self.results['database']['indexes']}")
        print(f"Пинг до Telegram: {self.results['network']['ping_telegram_ms']} ms")
        
        if self.results['optimizations']:
            print("\n⚡ РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ:")
            for opt in self.results['optimizations']:
                print(f"  {opt}")
        
        return self.results

if __name__ == "__main__":
    diag = UltimateDiagnostic()
    diag.run_all()
