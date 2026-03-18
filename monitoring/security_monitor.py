#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime

LOG_FILE = "/root/ulibka_eco_v2/logs/security.log"

def check_failed_logins():
    result = subprocess.run(
        ['journalctl', '-u', 'ssh', '--since', '1 hour ago'],
        capture_output=True, text=True
    )
    return result.stdout.count('Failed password')

def check_fail2ban():
    result = subprocess.run(
        ['fail2ban-client', 'status', 'sshd'],
        capture_output=True, text=True
    )
    banned = 0
    for line in result.stdout.split('\n'):
        if 'Banned IP list' in line:
            banned = len(line.split(':')) if ':' in line else 0
    return banned

def main():
    data = {
        'timestamp': datetime.now().isoformat(),
        'failed_logins': check_failed_logins(),
        'banned_ips': check_fail2ban()
    }
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(data) + '\n')
    print(f"✅ Мониторинг: {data}")

if __name__ == "__main__":
    main()
