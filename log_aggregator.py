#!/usr/bin/env python3
"""
Агрегатор логов для экосистемы Улыбка
"""

import os
import json
import logging
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("log_aggregator")


class LogAggregator:
    """Сбор и агрегация логов ботов"""
    
    def __init__(self, log_dir: str = "/var/log/smile_ecosystem"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_metrics(self) -> Dict:
        """Сбор метрик из логов"""
        metrics = {
            "total_lines": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "bots": {}
        }
        
        for log_file in self.log_dir.glob("*.log"):
            bot_name = log_file.stem.replace("_bot", "")
            metrics["bots"][bot_name] = {"errors": 0, "warnings": 0, "lines": 0}
            
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            metrics["bots"][bot_name]["lines"] += 1
                            metrics["total_lines"] += 1
                            if "ERROR" in line:
                                metrics["bots"][bot_name]["errors"] += 1
                                metrics["total_errors"] += 1
                            if "WARNING" in line:
                                metrics["bots"][bot_name]["warnings"] += 1
                                metrics["total_warnings"] += 1
                except Exception as e:
                    logger.error(f"Failed to read {log_file}: {e}")
        
        return metrics
    
    def get_error_summary(self, hours: int = 24) -> Dict:
        """Получение сводки по ошибкам за период"""
        cutoff = datetime.now() - timedelta(hours=hours)
        errors = []
        
        for log_file in self.log_dir.glob("*.log"):
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            if "ERROR" in line or "CRITICAL" in line:
                                errors.append({
                                    "file": log_file.stem,
                                    "line": line.strip()[:200],
                                    "timestamp": datetime.now().isoformat()
                                })
                except Exception:
                    pass
        
        return {
            "total": len(errors),
            "errors": errors[:50],
            "period_hours": hours
        }
    
    def generate_report(self) -> Dict:
        """Генерация полного отчёта"""
        metrics = self.collect_metrics()
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "summary": {
                "total_bots_with_logs": len([b for b in metrics["bots"].values() if b["lines"] > 0]),
                "error_rate": metrics["total_errors"] / max(metrics["total_lines"], 1),
                "warning_rate": metrics["total_warnings"] / max(metrics["total_lines"], 1)
            }
        }

if __name__ == "__main__":
    agg = LogAggregator()
    print(json.dumps(agg.generate_report(), indent=2))
