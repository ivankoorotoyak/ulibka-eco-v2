#!/bin/bash
# Скрипт обновления проекта
cd /root/ulibka_eco_v2

echo "🔄 Обновление проекта..."
echo "Время: $(date)"

# Сохраняем текущее состояние для отката
BACKUP_DIR="/root/backups/pre-deploy-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r . "$BACKUP_DIR" 2>/dev/null

# Получаем последние изменения
git pull origin main

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем зависимости
pip install -r requirements.txt 2>/dev/null || echo "⚠️ Нет requirements.txt"

# Запускаем тесты (если есть)
if [ -f "tests/run_tests.sh" ]; then
    ./tests/run_tests.sh
fi

# Перезапускаем ботов
/root/start_bots_final.sh

# Перезапускаем сервисы
sudo systemctl restart self-healing
sudo systemctl restart bot_exporter

echo "✅ Обновление завершено"
