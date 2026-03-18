#!/usr/bin/env python3
"""
Self-Healing System — автоматическое восстановление ботов
"""
import os
import sys
import time
import json
import subprocess
import threading
import requests
from datetime import datetime, timedelta
from pathlib import Path

class SelfHealing:
    def __init__(self):
        self.bots = [
            {'name': 'plus', 'dir': 'ulibka_plusbot', 'token_key': 'MAIN_BOT_TOKEN'},
            {'name': 'joke', 'dir': 'ulibka_jokebot', 'token_key': 'JOKE_BOT_TOKEN'},
            {'name': 'clean', 'dir': 'ulibka_cleanbot', 'token_key': 'CLEAN_BOT_TOKEN'},
            {'name': 'implant', 'dir': 'ulibka_implantbot', 'token_key': 'IMPLANT_BOT_TOKEN'},
            {'name': 'kid', 'dir': 'ulibka_kidbot', 'token_key': 'KID_BOT_TOKEN'},
            {'name': 'philo', 'dir': 'ulibka_philobot', 'token_key': 'PHILOSOPHER_BOT_TOKEN'},
            {'name': 'prof', 'dir': 'ulibka_profbot', 'token_key': 'PROF_BOT_TOKEN'},
            {'name': 'karta', 'dir': 'stomkartabot', 'token_key': 'KARTA_BOT_TOKEN'},
            {'name': 'dentai', 'dir': 'dentai_help_bot', 'token_key': 'DENTIST_BOT_TOKEN'},
            {'name': 'admin', 'dir': 'admin_bot', 'token_key': 'ADMIN_BOT_TOKEN'},
        ]
        
        self.base_dir = Path("/root/ulibka_eco")
        self.healing_log = Path("/root/ulibka_eco_v2/self-healing/logs/healing.log")
        self.alerts_log = Path("/root/ulibka_eco_v2/self-healing/logs/alerts.log")
        self.history_dir = Path("/root/ulibka_eco_v2/self-healing/history")
        
        # Статистика
        self.stats = {
            'checks': 0,
            'healed': 0,
            'failed': 0,
            'alerts': 0
        }
        
        # Загружаем статистику
        self.load_stats()
    
    def load_stats(self):
        """Загрузка статистики"""
        stats_file = self.history_dir / 'stats.json'
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    self.stats = json.load(f)
            except:
                pass
    
    def save_stats(self):
        """Сохранение статистики"""
        stats_file = self.history_dir / 'stats.json'
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def log(self, message, level='INFO'):
        """Логирование"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.healing_log, 'a') as f:
            f.write(log_entry)
        
        if level == 'ERROR':
            print(f"❌ {message}")
        elif level == 'WARNING':
            print(f"⚠️ {message}")
        elif level == 'SUCCESS':
            print(f"✅ {message}")
        else:
            print(f"ℹ️ {message}")
    
    def alert(self, message, level='WARNING'):
        """Отправка алерта (в лог и Telegram)"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alert_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.alerts_log, 'a') as f:
            f.write(alert_entry)
        
        self.stats['alerts'] += 1
        self.save_stats()
        
        # Отправка в Telegram (если есть статус-бот)
        self.send_telegram_alert(message, level)
    
    def send_telegram_alert(self, message, level):
        """Отправка алерта в Telegram"""
        try:
            token = "8756485893:AAHSaXhpdY9cCv91D_PMA6oBymTp8RH7miE"
            chat_id = 8052686185
            
            emoji = {
                'INFO': 'ℹ️',
                'WARNING': '⚠️',
                'ERROR': '🚨',
                'SUCCESS': '✅'
            }
            
            text = f"{emoji.get(level, 'ℹ️')} *Self-Healing Alert*\n"
            text += f"`{message}`"
            
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data={
                    'chat_id': chat_id,
                    'text': text,
                    'parse_mode': 'Markdown'
                },
                timeout=3
            )
        except:
            pass
    
    def check_bot_screen(self, bot_name):
        """Проверка, запущен ли бот в screen"""
        result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        return f"{bot_name}_bot" in result.stdout
    
    def check_bot_process(self, bot_dir):
        """Проверка, есть ли процесс бота"""
        result = subprocess.run(
            ['pgrep', '-f', f"{bot_dir}/bot.py"],
            capture_output=True, text=True
        )
        return result.returncode == 0
    
    def check_bot_api(self, token):
        """Проверка через Telegram API"""
        try:
            r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=3)
            return r.status_code == 200 and r.json().get('ok', False)
        except:
            return False
    
    def start_bot(self, bot):
        """Запуск бота"""
        try:
            cmd = f"cd /root/ulibka_eco/{bot['dir']} && screen -dmS {bot['name']}_bot python3 bot.py"
            subprocess.run(cmd, shell=True, check=True)
            self.log(f"Бот {bot['name']} запущен", 'SUCCESS')
            self.stats['healed'] += 1
            return True
        except Exception as e:
            self.log(f"Ошибка запуска {bot['name']}: {e}", 'ERROR')
            self.stats['failed'] += 1
            return False
    
    def kill_bot(self, bot_name):
        """Убить процесс бота"""
        subprocess.run(['pkill', '-f', f"{bot_name}_bot"], stderr=subprocess.DEVNULL)
        subprocess.run(['screen', '-S', f"{bot_name}_bot", '-X', 'quit'], stderr=subprocess.DEVNULL)
        self.log(f"Бот {bot_name} остановлен", 'INFO')
    
    def restart_bot(self, bot):
        """Перезапуск бота"""
        self.kill_bot(bot['name'])
        time.sleep(1)
        return self.start_bot(bot)
    
    def check_bot_health(self, bot):
        """Полная проверка здоровья бота"""
        issues = []
        
        # Проверка через screen
        if not self.check_bot_screen(bot['name']):
            issues.append("screen")
        
        # Проверка через процессы
        if not self.check_bot_process(bot['dir']):
            issues.append("process")
        
        # Если есть проблемы, пробуем восстановить
        if issues:
            self.log(f"Бот {bot['name']} имеет проблемы: {issues}", 'WARNING')
            
            # Пробуем перезапустить
            if self.restart_bot(bot):
                self.alert(f"Бот {bot['name']} восстановлен (были проблемы: {issues})", 'SUCCESS')
                return True
            else:
                self.alert(f"НЕ удалось восстановить бота {bot['name']}!", 'ERROR')
                return False
        else:
            self.log(f"Бот {bot['name']} работает нормально", 'INFO')
            return True
    
    def collect_metrics(self):
        """Сбор метрик о состоянии"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'bots': {},
            'system': self.get_system_metrics()
        }
        
        for bot in self.bots:
            metrics['bots'][bot['name']] = {
                'screen': self.check_bot_screen(bot['name']),
                'process': self.check_bot_process(bot['dir']),
                'healthy': self.check_bot_screen(bot['name']) and self.check_bot_process(bot['dir'])
            }
        
        # Сохраняем в историю
        filename = self.history_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def get_system_metrics(self):
        """Системные метрики"""
        import psutil
        return {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
    
    def heal_all(self):
        """Проверка и восстановление всех ботов"""
        self.log("=" * 50)
        self.log("ЗАПУСК ПРОВЕРКИ ВСЕХ БОТОВ", 'INFO')
        
        self.stats['checks'] += 1
        healthy = 0
        
        for bot in self.bots:
            if self.check_bot_health(bot):
                healthy += 1
            time.sleep(0.5)
        
        self.log(f"ИТОГ: {healthy}/{len(self.bots)} ботов работают", 'INFO')
        self.save_stats()
        
        # Собираем метрики
        self.collect_metrics()
    
    def watch_loop(self):
        """Постоянный цикл мониторинга"""
        self.log("🚀 Запуск постоянного мониторинга (проверка каждые 30 сек)")
        
        while True:
            try:
                self.heal_all()
                time.sleep(30)
            except KeyboardInterrupt:
                self.log("🛑 Мониторинг остановлен")
                break
            except Exception as e:
                self.log(f"Ошибка в цикле: {e}", 'ERROR')
                time.sleep(5)

if __name__ == "__main__":
    healer = SelfHealing()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        healer.watch_loop()
    else:
        healer.heal_all()
