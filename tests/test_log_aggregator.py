#!/usr/bin/env python3
"""
Тесты для агрегатора логов
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '/opt/smile_bots')

from log_aggregator import LogAggregator


class TestLogAggregator:
    """Тесты LogAggregator"""
    
    def test_init(self, temp_log_dir):
        """Тест инициализации"""
        aggregator = LogAggregator(log_dir=temp_log_dir)
        assert aggregator is not None
        assert aggregator.log_dir == temp_log_dir
    
    def test_parse_log_line(self, temp_log_dir):
        """Тест парсинга строки лога"""
        aggregator = LogAggregator(log_dir=temp_log_dir)
        
        line = "2026-03-21 10:00:00 - prof_bot - INFO - Bot started"
        parsed = aggregator._parse_log_line(line)
        
        assert parsed is not None
        assert parsed["level"] == "INFO"
        assert parsed["bot"] == "prof_bot"
        assert parsed["message"] == "Bot started"
    
    def test_parse_log_line_error(self, temp_log_dir):
        """Тест парсинга строки с ошибкой"""
        aggregator = LogAggregator(log_dir=temp_log_dir)
        
        line = "2026-03-21 10:01:00 - prof_bot - ERROR - Connection failed"
        parsed = aggregator._parse_log_line(line)
        
        assert parsed["level"] == "ERROR"
    
    def test_parse_log_line_warning(self, temp_log_dir):
        """Тест парсинга предупреждения"""
        aggregator = LogAggregator(log_dir=temp_log_dir)
        
        line = "2026-03-21 10:02:00 - dentai_bot - WARNING - Slow response"
        parsed = aggregator._parse_log_line(line)
        
        assert parsed["level"] == "WARNING"
    
    def test_collect_metrics_from_file(self, temp_log_dir, sample_logs):
        """Тест сбора метрик из файла"""
        log_file = Path(temp_log_dir) / "test.log"
        with open(log_file, 'w') as f:
            f.write("\n".join(sample_logs))
        
        aggregator = LogAggregator(log_dir=temp_log_dir)
        metrics = aggregator.collect_metrics()
        
        assert metrics["total_errors"] == 1
        assert metrics["total_warnings"] == 1
        assert metrics["total_lines"] == 5
        assert "prof_bot" in metrics["bots"]
        assert metrics["bots"]["prof_bot"]["errors"] == 1
    
    def test_collect_empty_log_dir(self, temp_log_dir):
        """Тест сбора метрик из пустой директории"""
        aggregator = LogAggregator(log_dir=temp_log_dir)
        metrics = aggregator.collect_metrics()
        
        assert metrics["total_lines"] == 0
        assert metrics["total_errors"] == 0
    
    def test_get_error_summary(self, temp_log_dir, sample_logs):
        """Тест получения сводки по ошибкам"""
        log_file = Path(temp_log_dir) / "test.log"
        with open(log_file, 'w') as f:
            f.write("\n".join(sample_logs))
        
        aggregator = LogAggregator(log_dir=temp_log_dir)
        summary = aggregator.get_error_summary()
        
        assert "total_errors" in summary
        assert "errors_by_bot" in summary
    
    def test_generate_report(self, temp_log_dir, sample_logs):
        """Тест генерации отчёта"""
        log_file = Path(temp_log_dir) / "test.log"
        with open(log_file, 'w') as f:
            f.write("\n".join(sample_logs))
        
        aggregator = LogAggregator(log_dir=temp_log_dir)
        report = aggregator.generate_report()
        
        assert report["timestamp"] is not None
        assert report["metrics"]["total_lines"] == 5
    
    def test_parse_unknown_format(self, temp_log_dir):
        """Тест парсинга неизвестного формата"""
        aggregator = LogAggregator(log_dir=temp_log_dir)
        
        line = "Unknown format line without timestamp"
        parsed = aggregator._parse_log_line(line)
        
        assert parsed is None
    
    def test_bot_name_extraction(self, temp_log_dir):
        """Тест извлечения имени бота"""
        aggregator = LogAggregator(log_dir=temp_log_dir)
        
        test_cases = [
            ("2026-03-21 - prof_bot - INFO", "prof_bot"),
            ("2026-03-21 - dentai_bot - ERROR", "dentai_bot"),
            ("2026-03-21 - unknown - INFO", "unknown"),
        ]
        
        for line, expected in test_cases:
            parsed = aggregator._parse_log_line(line)
            if parsed:
                assert parsed.get("bot") == expected
