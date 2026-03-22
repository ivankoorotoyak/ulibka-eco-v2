#!/bin/bash
# Ежедневный запуск тестов с отчётом

TEST_DIR="/opt/smile_bots/tests"
LOG_DIR="/var/log/smile_ecosystem"
REPORT_FILE="${LOG_DIR}/test_report_$(date +%Y%m%d).log"
VENV_PYTHON="/root/bot_venv/bin/python"

cd $TEST_DIR

echo "=== ТЕСТИРОВАНИЕ ЭКОСИСТЕМЫ $(date) ===" | tee -a $REPORT_FILE
echo "" | tee -a $REPORT_FILE

# Запуск тестов с coverage
$VENV_PYTHON -m pytest -v --tb=short --cov=/opt/smile_bots --cov-report=term --cov-report=html:/opt/smile_bots/tests/coverage 2>&1 | tee -a $REPORT_FILE

# Проверка результата
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "" | tee -a $REPORT_FILE
    echo "✅ Все тесты пройдены успешно" | tee -a $REPORT_FILE
else
    echo "" | tee -a $REPORT_FILE
    echo "❌ Некоторые тесты не пройдены" | tee -a $REPORT_FILE
fi

echo "" | tee -a $REPORT_FILE
echo "=== КОНЕЦ ТЕСТИРОВАНИЯ ===" | tee -a $REPORT_FILE
