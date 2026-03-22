#!/usr/bin/env python3
"""
Веб-дашборд для мониторинга экосистемы
"""

import os
import json
import time
import psutil
from datetime import datetime
from pathlib import Path

try:
    from flask import Flask, jsonify, Response, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Run: pip install flask")

from metrics import get_metrics, PROMETHEUS_AVAILABLE
from state_manager import StateManager

STATE_FILE = "/opt/smile_bots/ecosystem_state.json"
PORT = int(os.getenv("DASHBOARD_PORT", 5000))

app = Flask(__name__)
state_manager = StateManager(STATE_FILE)
metrics = get_metrics()

# Простой HTML шаблон
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Экосистема Улыбка - Дашборд</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="container mt-4">
        <h1 class="mb-4">🌍 Экосистема Улыбка</h1>
        
        <!-- Health Summary -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>Общий статус</h5>
                        <h2 class="text-{{ 'success' if overall_status == 'HEALTHY' else 'warning' if overall_status == 'WARNING' else 'danger' }}">
                            {{ overall_status }}
                        </h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>Скоринг</h5>
                        <h2>{{ score }}/100</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>Активные боты</h5>
                        <h2>{{ active_bots }}/{{ total_bots }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>Uptime</h5>
                        <h2>{{ uptime }}ч</h2>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Bots Status -->
        <div class="card mb-4">
            <div class="card-header">
                <h5>🤖 Статус ботов</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for bot_name, bot_info in bots.items() %}
                    <div class="col-md-3 col-sm-6 mb-2">
                        <span class="badge bg-{{ 'success' if bot_info.get('status') == 'active' else 'danger' }}">
                            {{ '●' if bot_info.get('status') == 'active' else '○' }}
                        </span>
                        <strong>{{ bot_name }}</strong>
                        <br>
                        <small class="text-muted">{{ bot_info.get('status', 'unknown') }}</small>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <!-- Infrastructure -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>💻 Инфраструктура</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Диск:</strong> {{ disk_used }}% использовано</p>
                        <div class="progress mb-3">
                            <div class="progress-bar" style="width: {{ disk_used }}%"></div>
                        </div>
                        <p><strong>RAM:</strong> {{ ram_used }}% использовано</p>
                        <div class="progress mb-3">
                            <div class="progress-bar" style="width: {{ ram_used }}%"></div>
                        </div>
                        <p><strong>CPU:</strong> {{ cpu_used }}%</p>
                        <div class="progress">
                            <div class="progress-bar" style="width: {{ cpu_used }}%"></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>📊 Метрики</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Всего запросов:</strong> {{ total_requests }}</p>
                        <p><strong>Ошибок:</strong> {{ total_errors }}</p>
                        <p><strong>Prometheus:</strong> 
                            <span class="badge bg-{{ 'success' if prometheus_available else 'secondary' }}">
                                {{ 'доступен' if prometheus_available else 'не установлен' }}
                            </span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="text-center text-muted mt-4 mb-3">
            <small>Обновлено: {{ timestamp }} | 
                <a href="/metrics">/metrics</a> | 
                <a href="/health">/health</a> | 
                <a href="/api/state">/api/state</a>
            </small>
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """Главная страница"""
    state = state_manager.state
    bots = state.get("bots", {})
    
    active_bots = sum(1 for b in bots.values() if b.get("status") == "active")
    total_bots = len(bots)
    
    metrics_data = metrics.get_metrics_dict()
    
    disk = psutil.disk_usage('/')
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)
    
    # Подсчёт запросов и ошибок
    total_requests = 0
    total_errors = 0
    for bot_data in metrics_data.get("requests", {}).values():
        total_requests += sum(bot_data.values())
    for bot_data in metrics_data.get("errors", {}).values():
        total_errors += sum(bot_data.values())
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        overall_status=state.get("overall_status", "HEALTHY"),
        score=state.get("score", 100),
        active_bots=active_bots,
        total_bots=total_bots,
        uptime=round(metrics_data.get("uptime", 0) / 3600, 1),
        bots=bots,
        disk_used=disk.percent,
        ram_used=memory.percent,
        cpu_used=cpu,
        total_requests=total_requests,
        total_errors=total_errors,
        prometheus_available=PROMETHEUS_AVAILABLE,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@app.route('/metrics')
def metrics_endpoint():
    """Prometheus метрики"""
    if PROMETHEUS_AVAILABLE:
        return Response(metrics.get_prometheus_metrics(), mimetype="text/plain; version=0.0.4")
    return Response("# Prometheus client not available\n", mimetype="text/plain")


@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bots": len(state_manager.state.get("bots", {})),
        "prometheus": PROMETHEUS_AVAILABLE,
        "flask": FLASK_AVAILABLE
    })


@app.route('/api/state')
def api_state():
    """API состояния"""
    return jsonify(state_manager.state)


if __name__ == "__main__":
    if not FLASK_AVAILABLE:
        print("❌ Flask not installed")
        exit(1)
    
    print(f"🚀 Dashboard starting on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
