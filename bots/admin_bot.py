#!/usr/bin/env python3
"""
Админ-бот версии 2.0 для управления экосистемой «Вселенная Улыбка»
Функции:
- Статус всех 12 ботов (screen + systemd)
- Управление inclusive_bot (запуск/стоп/рестарт)
- Статистика каналов
- Мониторинг голосовых функций
- Просмотр логов
- Управление бэкапами
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
sys.path.append('/root/ulibka-eco-v2')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '8711144543:AAGLDe6X3VInsfAHBo7YnU3EZ_u8jhHw04U')
ADMIN_ID = os.environ.get('ADMIN_ID', '8052686185')

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def run_command(cmd: str) -> str:
    """Выполняет команду и возвращает вывод"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except Exception as e:
        return f"❌ Ошибка: {e}"

def get_screen_bots() -> list:
    """Возвращает список ботов в screen"""
    output = run_command("screen -ls | grep -E 'ulibka|dentai|stomkarta|admin' || true")
    bots = []
    for line in output.split('\n'):
        if '.' in line:
            parts = line.strip().split()
            if len(parts) >= 1:
                bot_id = parts[0].split('.')[0]
                bot_name = parts[0].split('.')[1] if '.' in parts[0] else 'unknown'
                bots.append({'id': bot_id, 'name': bot_name, 'full': line})
    return bots

def get_systemd_status() -> dict:
    """Возвращает статус systemd сервисов"""
    services = ['inclusive-bot.service', 'admin-bot.service']
    status = {}
    for service in services:
        output = run_command(f"systemctl is-active {service} 2>/dev/null || echo 'inactive'")
        status[service] = output.strip()
    return status

def get_lockbox_count() -> int:
    """Возвращает количество секретов в Lockbox"""
    output = run_command("yc lockbox secret list --format json 2>/dev/null | jq '. | length' || echo 0")
    try:
        return int(output.strip())
    except:
        return 0

def get_backup_count() -> int:
    """Возвращает количество бэкапов"""
    output = run_command("ls -1 /root/backups/ 2>/dev/null | wc -l")
    try:
        return int(output.strip())
    except:
        return 0

def get_users_count() -> int:
    """Возвращает количество пользователей в БД"""
    output = run_command("sqlite3 /var/lib/ulibka/ulibka.db 'SELECT COUNT(*) FROM users;' 2>/dev/null || echo 0")
    try:
        return int(output.strip())
    except:
        return 0

# ========== ОСНОВНЫЕ ОБРАБОТЧИКИ ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("🤖 Статус ботов", callback_data="status_bots")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("🎤 inclusive_bot", callback_data="inclusive_menu")],
        [InlineKeyboardButton("📢 Каналы", callback_data="channels")],
        [InlineKeyboardButton("💾 Бэкапы", callback_data="backups")],
        [InlineKeyboardButton("📋 Логи", callback_data="logs")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 **Я админ-бот системы Улыбка+**\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "status_bots":
        # Статус всех ботов
        screen_bots = get_screen_bots()
        systemd = get_systemd_status()
        
        text = "**🤖 СТАТУС БОТОВ**\n\n"
        text += f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        text += "**🖥️ Screen боты:**\n"
        for bot in screen_bots:
            text += f"✅ {bot['name']}\n"
        
        text += f"\n**⚙️ Systemd боты:**\n"
        for service, status in systemd.items():
            emoji = "✅" if status == "active" else "❌"
            text += f"{emoji} {service.replace('.service', '')}: {status}\n"
        
        text += f"\n**📊 Всего:** {len(screen_bots)} в screen, {sum(1 for s in systemd.values() if s=='active')} в systemd"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "stats":
        # Общая статистика
        screen_count = len(get_screen_bots())
        systemd = get_systemd_status()
        lockbox = get_lockbox_count()
        backups = get_backup_count()
        users = get_users_count()
        
        text = "**📊 ОБЩАЯ СТАТИСТИКА**\n\n"
        text += f"🤖 **Боты:** {screen_count} в screen, {sum(1 for s in systemd.values() if s=='active')} в systemd\n"
        text += f"🔐 **Lockbox секретов:** {lockbox}\n"
        text += f"💾 **Бэкапов:** {backups}\n"
        text += f"👥 **Пользователей в БД:** {users}\n"
        text += f"📢 **Каналов:** 9 (по конфигурации)\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "inclusive_menu":
        # Меню inclusive_bot
        status = run_command("systemctl is-active inclusive-bot.service 2>/dev/null || echo 'inactive'").strip()
        emoji = "✅" if status == "active" else "❌"
        
        text = f"**🎤 inclusive_bot**\n\n"
        text += f"Статус: {emoji} {status}\n\n"
        text += "Выберите действие:"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Перезапустить", callback_data="inclusive_restart")],
            [InlineKeyboardButton("📋 Логи", callback_data="inclusive_logs")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "inclusive_restart":
        await query.edit_message_text("🔄 Перезапускаю inclusive_bot...")
        run_command("systemctl restart inclusive-bot.service")
        await asyncio.sleep(2)
        status = run_command("systemctl is-active inclusive-bot.service 2>/dev/null || echo 'inactive'").strip()
        await query.edit_message_text(f"✅ inclusive_bot перезапущен. Статус: {status}")
    
    elif query.data == "inclusive_logs":
        logs = run_command("journalctl -u inclusive-bot.service -n 20 --no-pager")
        if len(logs) > 4000:
            logs = logs[:4000] + "...\n(обрезано)"
        await query.edit_message_text(f"**📋 Логи inclusive_bot:**\n```\n{logs}\n```", parse_mode='Markdown')
    
    elif query.data == "channels":
        # Проверка каналов
        if os.path.exists("/root/channels.conf"):
            with open("/root/channels.conf", 'r') as f:
                channels = f.read()
            text = f"**📢 КАНАЛЫ**\n\n```\n{channels}\n```"
        else:
            text = "❌ Файл channels.conf не найден"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "backups":
        # Информация о бэкапах
        backups = run_command("ls -la /root/backups/ | tail -10")
        text = f"**💾 БЭКАПЫ**\n\n```\n{backups}\n```"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Создать бэкап сейчас", callback_data="backup_now")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "backup_now":
        await query.edit_message_text("🔄 Создаю бэкап...")
        result = run_command("/root/backup_to_cloud.sh")
        await query.edit_message_text(f"✅ Бэкап создан:\n```\n{result[:500]}\n```", parse_mode='Markdown')
    
    elif query.data == "logs":
        # Выбор логов
        keyboard = [
            [InlineKeyboardButton("📋 inclusive_bot", callback_data="log_inclusive")],
            [InlineKeyboardButton("📋 admin_bot", callback_data="log_admin")],
            [InlineKeyboardButton("📋 screen боты", callback_data="log_screen")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")],
        ]
        await query.edit_message_text("**📋 Выберите логи:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "log_inclusive":
        logs = run_command("journalctl -u inclusive-bot.service -n 30 --no-pager")
        if len(logs) > 4000:
            logs = logs[:4000] + "...\n(обрезано)"
        await query.edit_message_text(f"**inclusive_bot логи:**\n```\n{logs}\n```", parse_mode='Markdown')
    
    elif query.data == "log_admin":
        logs = run_command("journalctl -u admin-bot.service -n 30 --no-pager 2>/dev/null || echo 'Нет логов'")
        await query.edit_message_text(f"**admin_bot логи:**\n```\n{logs}\n```", parse_mode='Markdown')
    
    elif query.data == "log_screen":
        logs = run_command("for pid in $(screen -ls | grep -Eo '[0-9]+' | head -3); do echo '=== Бот $pid ==='; cat /tmp/*.log 2>/dev/null | tail -5; done")
        await query.edit_message_text(f"**screen боты (последние логи):**\n```\n{logs}\n```", parse_mode='Markdown')
    
    elif query.data == "back":
        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🤖 Статус ботов", callback_data="status_bots")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("🎤 inclusive_bot", callback_data="inclusive_menu")],
            [InlineKeyboardButton("📢 Каналы", callback_data="channels")],
            [InlineKeyboardButton("💾 Бэкапы", callback_data="backups")],
            [InlineKeyboardButton("📋 Логи", callback_data="logs")],
        ]
        await query.edit_message_text(
            "👋 **Я админ-бот системы Улыбка+**\n\nВыберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# ========== ЗАПУСК ==========

async def post_init(application: Application):
    """Действия после запуска"""
    logger.info("✅ Админ-бот версии 2.0 запущен")
    print("✅ Админ-бот версии 2.0 запущен")

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 Запуск админ-бота...")
    app.run_polling()

if __name__ == "__main__":
    main()
