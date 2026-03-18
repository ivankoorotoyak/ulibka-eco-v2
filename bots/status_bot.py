#!/usr/bin/env python3
"""
Статус-бот для мониторинга системы
"""
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Конфигурация
TOKEN = "8756485893:AAHSaXhpdY9cCv91D_PMA6oBymTp8RH7miE"
ADMIN_ID = 8052686185

# Цветовые статусы
STATUS_EMOJI = {
    'online': '🟢',
    'warning': '🟡',
    'offline': '🔴'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню статус-бота"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Этот бот только для администратора")
        return
    
    # Собираем информацию о системе
    bots_count = 0
    try:
        result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        bots_count = result.stdout.count('Detached')
    except:
        pass
    
    # Информация о диске
    disk = subprocess.run(['df', '-h', '/'], capture_output=True, text=True).stdout.split('\n')[1].split()
    disk_used = disk[4] if len(disk) > 4 else '0%'
    
    keyboard = [
        [InlineKeyboardButton("📊 Статус ботов", callback_data='bots')],
        [InlineKeyboardButton("💻 Система", callback_data='system')],
        [InlineKeyboardButton("📦 Бэкапы", callback_data='backups')],
    ]
    
    await update.message.reply_text(
        f"👋 *Привет, Администратор!*\n\n"
        f"📊 *Текущий статус:*\n"
        f"🤖 Ботов запущено: {bots_count}\n"
        f"💾 Диск: {disk_used}\n"
        f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}\n\n"
        f"Выберите раздел:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'bots':
        result = subprocess.run(['screen', '-ls'], capture_output=True, text=True)
        await query.edit_message_text(f"🤖 *Статус ботов:*\n```\n{result.stdout}\n```", parse_mode='Markdown')
    
    elif query.data == 'system':
        # Информация о системе
        cpu = subprocess.run(['top', '-bn1'], capture_output=True, text=True).stdout
        mem = subprocess.run(['free', '-h'], capture_output=True, text=True).stdout
        disk = subprocess.run(['df', '-h'], capture_output=True, text=True).stdout
        await query.edit_message_text(f"💻 *Система:*\n```\nCPU: {cpu[:200]}...\n\n{mem}\n\n{disk[:200]}...\n```", parse_mode='Markdown')
    
    elif query.data == 'backups':
        result = subprocess.run(['ls', '-la', '/root/backups/'], capture_output=True, text=True)
        await query.edit_message_text(f"📦 *Бэкапы:*\n```\n{result.stdout}\n```", parse_mode='Markdown')
    
    # Кнопка назад
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back')]]
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

def main():
    print("🚀 Запуск статус-бота @vanxo2030bot...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern='^(?!back$).*'))
    app.add_handler(CallbackQueryHandler(back, pattern='^back$'))
    app.run_polling()

if __name__ == "__main__":
    main()
