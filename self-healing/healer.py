#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

class SelfHealing:
    def __init__(self):
        self.bots = [
            {'name': 'plus', 'dir': '/root/ulibka_eco/ulibka_plusbot', 'cmd': 'plus_bot'},
            {'name': 'joke', 'dir': '/root/ulibka_eco/ulibka_jokebot', 'cmd': 'joke_bot'},
            {'name': 'clean', 'dir': '/root/ulibka_eco/ulibka_cleanbot', 'cmd': 'clean_bot'},
            {'name': 'implant', 'dir': '/root/ulibka_eco/ulibka_implantbot', 'cmd': 'implant_bot'},
            {'name': 'kid', 'dir': '/root/ulibka_eco/ulibka_kidbot', 'cmd': 'kid_bot'},
            {'name': 'philo', 'dir': '/root/ulibka_eco/ulibka_philobot', 'cmd': 'philo_bot'},
            {'name': 'prof', 'dir': '/root/ulibka_eco/ulibka_profbot', 'cmd': 'prof_bot'},
            {'name': 'karta', 'dir': '/root/ulibka_eco/stomkartabot', 'cmd': 'karta_bot'},
            {'name': 'dentai', 'dir': '/root/ulibka_eco/dentai_help_bot', 'cmd': 'dentai_bot'},
            {'name': 'admin', 'dir': '/root/ulibka_eco/admin_bot', 'cmd': 'admin_bot'},
        ]
        self.log_file = Path("/root/ulibka_eco_v2/self-healing/logs/healing.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, msg, level='INFO'):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"[{ts}] [{level}] {msg}\n")
        print(f"[{ts}] [{level}] {msg}")
    
    def check_bot(self, bot):
        if not os.path.exists(bot['dir']):
            self.log(f"❌ Папка {bot['dir']} не существует!", 'ERROR')
            return False
        
        res = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        if bot['cmd'] not in res.stdout:
            self.log(f"🔄 Бот {bot['name']} не работает, перезапуск", 'WARNING')
            cmd = f"cd {bot['dir']} && screen -dmS {bot['cmd']} bash -c 'source /root/ulibka_eco/venv/bin/activate && python3 bot.py'"
            subprocess.run(cmd, shell=True)
            self.log(f"✅ Бот {bot['name']} перезапущен", 'SUCCESS')
            time.sleep(1)
        return True
    
    def heal_all(self):
        self.log("=" * 50)
        self.log("ПРОВЕРКА БОТОВ")
        for bot in self.bots:
            self.check_bot(bot)
            time.sleep(0.5)
        self.log("ПРОВЕРКА ЗАВЕРШЕНА")
    
    def watch(self):
        self.log("🚀 МОНИТОРИНГ ЗАПУЩЕН (каждые 30 сек)")
        while True:
            try:
                self.heal_all()
                time.sleep(30)
            except Exception as e:
                self.log(f"❌ Ошибка: {e}", 'ERROR')
                time.sleep(5)

if __name__ == "__main__":
    h = SelfHealing()
    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        h.watch()
    else:
        h.heal_all()
