#!/bin/bash
cd /root/ulibka_eco_v2
source venv/bin/activate

echo "⚡ Self-Healing System"
echo "══════════════════════"

# Запуск в screen
screen -dmS healer python3 self-healing/healer.py --watch

sleep 2
screen -ls | grep healer

echo -e "\n✅ Система самовосстановления запущена"
echo "   Проверка ботов каждые 30 секунд"
