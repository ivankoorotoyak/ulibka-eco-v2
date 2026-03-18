#!/bin/bash
# Статус деплоя
cd /root/ulibka_eco_v2

echo "📊 СТАТУС ПРОЕКТА"
echo "══════════════════"

# Текущая ветка
BRANCH=$(git branch --show-current)
echo "🌿 Ветка: $BRANCH"

# Последний коммит
COMMIT=$(git log -1 --pretty=format:"%h - %s, %cr")
echo "📝 Последний коммит: $COMMIT"

# Статус файлов
CHANGES=$(git status --porcelain | wc -l)
if [ $CHANGES -gt 0 ]; then
    echo "⚠️ Локальных изменений: $CHANGES"
else
    echo "✅ Нет локальных изменений"
fi

# Версия
if [ -f VERSION ]; then
    cat VERSION
else
    echo "📦 Версия: $(git describe --tags 2>/dev/null || echo 'dev')"
fi
