#!/usr/bin/env python3
import time
import requests

TOKENS = {
    'main': '8796290235:AAFpz_zkzJI-NXezHQ8NScY4rJe_3-beSQE',
    'joke': '8672286436:AAFal8P-u-7F3-8wPZ5p9LwPPS0X5K-igjI',
    'clean': '8733907654:AAG3eeKV4wiJpLPpZOec64ACeCGKX69GRU8',
}

print("\n⚡ ТЕСТ СКОРОСТИ БОТОВ")
print("=" * 40)

speeds = []
for name, token in TOKENS.items():
    start = time.time()
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=3)
        speed = (time.time() - start) * 1000
        if r.status_code == 200:
            print(f"✅ {name}: {speed:.0f} мс")
            speeds.append(speed)
    except:
        print(f"❌ {name}: ошибка")

if speeds:
    avg = sum(speeds) / len(speeds)
    print(f"\n⚡ Средняя скорость: {avg:.0f} мс")
    if avg < 300:
        print("✅ ОТЛИЧНО!")
    else:
        print("⚠️ НОРМАЛЬНО")
