#!/bin/bash
# Скрипт отката к предыдущей версии
cd /root/ulibka_eco_v2

LATEST_BACKUP=$(ls -dt /root/backups/pre-deploy-* | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ Нет бэкапов для отката"
    exit 1
fi

echo "🔄 Откат к $LATEST_BACKUP"

# Останавливаем сервисы
sudo systemctl stop self-healing
sudo systemctl stop bot_exporter

# Восстанавливаем
cp -r "$LATEST_BACKUP"/* .

# Перезапускаем
source venv/bin/activate
/root/start_bots_final.sh
sudo systemctl start self-healing
sudo systemctl start bot_exporter

echo "✅ Откат завершен"
