#!/usr/bin/env python3
"""
Тестирование скорости ответов ботов
"""
import time
import requests
from datetime import datetime

TOKENS = {
    'main': '8796290235:AAFpz_zkzJI-NXezHQ8NScY4rJe_3-beSQE',
    'joke': '8672286436:AAFal8P-u-7F3-8wPZ5p9LwPPS0X5K-igjI',
    'clean': '8733907654:AAG3eeKV4wiJpLPpZOec64ACeCGKX69GRU8',
}

def test_bot_speed(token, name):
    """Тестирует скорость ответа бота"""
    start = time.time()
    
    # Пробуем получить информацию о боте
    response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
    
    end = time.time()
    speed = (end - start) * 1000  # в миллисекундах
    
    if response.status_code == 200:
        return speed, True
    return speed, False

print("\n📊 ТЕСТ СКОРОСТИ БОТОВ")
print("=" * 50)

speeds = []
for name, token in TOKENS.items():
    speed, ok = test_bot_speed(token, name)
    if ok:
        print(f"✅ {name}: {speed:.0f} мс")
        speeds.append(speed)
    else:
        print(f"❌ {name}: ошибка")

if speeds:
    avg = sum(speeds) / len(speeds)
    print(f"\n⚡ Средняя скорость: {avg:.0f} мс")
    
    if avg < 200:
        print("✅ ОТЛИЧНО! Скорость высокая")
    elif avg < 400:
        print("⚠️ НОРМАЛЬНО, можно улучшить")
    else:
        print("❌ МЕДЛЕННО, нужна оптимизация")
