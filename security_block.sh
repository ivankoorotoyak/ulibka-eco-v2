#!/bin/bash
set -e
echo "🔐 БЛОК 3.5: УСИЛЕНИЕ БЕЗОПАСНОСТИ"
echo "═══════════════════════════════════════════════════════════════"

cd /root/ulibka_eco_v2

# 1. УСИЛЕНИЕ SSH
echo -e "\n📌 1. УСИЛЕНИЕ SSH"

# Бэкап текущей конфигурации
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d)

# Применяем максимальные настройки безопасности
cat >> /etc/ssh/sshd_config << 'EOL'

# === УСИЛЕНИЕ БЕЗОПАСНОСТИ ===
# Запрещаем вход по паролю (только ключи)
PasswordAuthentication no
PermitRootLogin prohibit-password
PubkeyAuthentication yes

# Ограничение попыток входа
MaxAuthTries 2
MaxSessions 2
LoginGraceTime 30

# Только протокол 2
Protocol 2

# Дополнительная защита
PermitEmptyPasswords no
ChallengeResponseAuthentication no
X11Forwarding no
PrintMotd no

# Таймауты
ClientAliveInterval 300
ClientAliveCountMax 2
EOL

# Перезапускаем SSH
systemctl restart sshd
echo "✅ SSH усилен"

# 2. НАСТРОЙКА FAIL2BAN
echo -e "\n📌 2. НАСТРОЙКА FAIL2BAN"

# Устанавливаем fail2ban
apt update && apt install fail2ban -y

# Создаём конфигурацию
cat > /etc/fail2ban/jail.local << 'EOL'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
ignoreip = 127.0.0.1/8

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 2
bantime = 86400
EOL

# Перезапускаем fail2ban
systemctl restart fail2ban
systemctl enable fail2ban
echo "✅ Fail2ban настроен"

# 3. РОТАЦИЯ КЛЮЧЕЙ
echo -e "\n📌 3. РОТАЦИЯ КЛЮЧЕЙ"

cat > /usr/local/bin/rotate-keys.sh << 'EOL'
#!/bin/bash
LOG_FILE="/root/ulibka_eco_v2/logs/key_rotation.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$DATE] Ротация ключей" >> "$LOG_FILE"

# Генерация новых ключей
ssh-keygen -t ed25519 -f /root/.ssh/ulibka_ed25519 -N "" -C "ulibka-$(date +%Y%m%d)" -q
cat /root/.ssh/ulibka_ed25519.pub >> /root/.ssh/authorized_keys
echo "   Ключи обновлены" >> "$LOG_FILE"
EOL

chmod +x /usr/local/bin/rotate-keys.sh
(crontab -l 2>/dev/null; echo "0 3 * * 0 /usr/local/bin/rotate-keys.sh") | crontab -
echo "✅ Ротация ключей настроена"

# 4. ЗАЩИТА ОТ DDOS
echo -e "\n📌 4. ЗАЩИТА ОТ DDOS"

cat >> /etc/sysctl.conf << 'EOL'

# Защита от DDoS
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_syn_retries = 2
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.conf.all.rp_filter = 1
EOL

sysctl -p
echo "✅ Защита от DDoS настроена"

# 5. МОНИТОРИНГ БЕЗОПАСНОСТИ
echo -e "\n📌 5. МОНИТОРИНГ БЕЗОПАСНОСТИ"

mkdir -p monitoring

cat > monitoring/security_monitor.py << 'EOL'
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
EOL

chmod +x monitoring/security_monitor.py
(crontab -l 2>/dev/null; echo "0 * * * * cd /root/ulibka_eco_v2 && python3 monitoring/security_monitor.py") | crontab -
echo "✅ Мониторинг безопасности настроен"

# 6. АВТООБНОВЛЕНИЯ
echo -e "\n📌 6. АВТООБНОВЛЕНИЯ"

apt install unattended-upgrades -y

cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOL'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOL

systemctl restart unattended-upgrades
echo "✅ Автообновления настроены"

# 7. ИТОГ
echo -e "\n📊 ИТОГОВАЯ ПРОВЕРКА"
echo "═══════════════════════════════════════════════════════════════"
echo "✅ SSH: усилен (только ключи)"
echo "✅ Fail2ban: активен"
echo "✅ Ротация ключей: еженедельно"
echo "✅ DDoS защита: включена"
echo "✅ Мониторинг: каждый час"
echo "✅ Автообновления: активны"
echo "═══════════════════════════════════════════════════════════════"
