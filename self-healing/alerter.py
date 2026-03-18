#!/usr/bin/env python3
"""
Отправка алертов в Telegram
"""
import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

class Alerter:
    def __init__(self):
        self.token = "8756485893:AAHSaXhpdY9cCv91D_PMA6oBymTp8RH7miE"
        self.chat_id = 8052686185
        self.log_file = Path("/root/ulibka_eco_v2/self-healing/logs/telegram.log")
    
    def send(self, message, level='INFO'):
        """Отправка сообщения"""
        emoji = {
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '🚨',
            'CRITICAL': '🔥'
        }
        
        text = f"{emoji.get(level, 'ℹ️')} *Self-Healing*\n"
        text += f"`{message}`"
        
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                data={
                    'chat_id': self.chat_id,
                    'text': text,
                    'parse_mode': 'Markdown'
                },
                timeout=5
            )
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.log_file, 'a') as f:
                f.write(f"[{timestamp}] [{level}] {message} (status: {r.status_code})\n")
            
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False

if __name__ == "__main__":
    alerter = Alerter()
    if len(sys.argv) > 2:
        alerter.send(sys.argv[2], sys.argv[1])
    else:
        print("Использование: python3 alerter.py LEVEL MESSAGE")
