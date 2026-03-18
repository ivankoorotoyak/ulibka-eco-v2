#!/usr/bin/env python3
"""
Полная диагностика системы
"""
import psutil
import subprocess
from datetime import datetime

print("🔍 ПОЛНАЯ ДИАГНОСТИКА СИСТЕМЫ")
print("=" * 50)
print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# CPU
cpu = psutil.cpu_percent(interval=1)
print(f"💻 CPU: {cpu}%")

# RAM
mem = psutil.virtual_memory()
print(f"🧠 RAM: {mem.percent}% ({mem.used//1024**3}/{mem.total//1024**3} GB)")

# Диск
disk = psutil.disk_usage('/')
print(f"💾 Диск: {disk.percent}% ({disk.used//1024**3}/{disk.total//1024**3} GB)")

# Боты
result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
bots = result.stdout.count('Detached')
print(f"🤖 Боты: {bots}/10")

# Redis
try:
    with open('/root/.redis_pass.txt', 'r') as f:
        redis_pass = f.read().strip()
    ping = subprocess.run(
        ['docker', 'exec', 'redis-ulibka', 'redis-cli', '-a', redis_pass, 'ping'],
        capture_output=True, text=True
    )
    redis_status = "✅" if 'PONG' in ping.stdout else "❌"
    print(f"🔴 Redis: {redis_status}")
except:
    print("🔴 Redis: ❌")

print("\n✅ Диагностика завершена")
