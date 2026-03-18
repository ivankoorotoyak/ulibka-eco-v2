#!/usr/bin/env python3
"""
Тест нагрузки на систему
"""
import time
import requests
import threading
from datetime import datetime

TOKENS = [
    '8796290235:AAFpz_zkzJI-NXezHQ8NScY4rJe_3-beSQE',
    '8672286436:AAFal8P-u-7F3-8wPZ5p9LwPPS0X5K-igjI',
    '8733907654:AAG3eeKV4wiJpLPpZOec64ACeCGKX69GRU8',
]

def test_bot(token, thread_id):
    """Тестирование одного бота"""
    results = []
    for i in range(10):  # 10 запросов
        start = time.time()
        try:
            r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
            speed = (time.time() - start) * 1000
            if r.status_code == 200:
                results.append(speed)
        except:
            pass
        time.sleep(0.1)
    
    if results:
        avg = sum(results) / len(results)
        print(f"   Поток {thread_id}: средняя скорость {avg:.0f} мс")
        return avg
    return 0

print("🚀 ЗАПУСК ТЕСТА НАГРУЗКИ (10 потоков)")
print("=" * 50)

threads = []
results = []

for i, token in enumerate(TOKENS * 3):  # 9 потоков
    t = threading.Thread(target=lambda: results.append(test_bot(token, i)))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

if results:
    total_avg = sum(results) / len(results)
    print(f"\n⚡ ИТОГОВАЯ СРЕДНЯЯ СКОРОСТЬ: {total_avg:.0f} мс")
    
    if total_avg < 200:
        print("✅ ОТЛИЧНО! Система выдерживает нагрузку")
    elif total_avg < 400:
        print("⚠️ НОРМАЛЬНО, но можно улучшить")
    else:
        print("❌ МЕДЛЕННО, нужна дополнительная оптимизация")
