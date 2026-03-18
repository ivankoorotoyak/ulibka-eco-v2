#!/usr/bin/env python3
"""
Молниеносный статус-бот с мониторингом ресурсов
"""
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from monitoring.fast_metrics import FastMetrics

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8756485893:AAHSaXhpdY9cCv91D_PMA6oBymTp8RH7miE"
ADMIN_ID = 8052686185

# Инициализируем быстрый сборщик метрик
metrics = FastMetrics()

# Эмодзи для статусов
STATUS = {
    'online': '🟢',
    'warning': '🟡',
    'offline': '🔴',
    'good': '✅',
    'bad': '❌'
}

def format_size(bytes):
    """Форматирование размера"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню (молниеносно)"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещён")
        return
    
    # Быстро получаем метрики
    m = metrics.get_all_metrics()
    
    # Формируем статус
    bot_status = STATUS['good'] if m['bots']['active'] >= 9 else STATUS['bad']
    redis_status = STATUS['online'] if m['redis']['status'] == 'online' else STATUS['offline']
    disk_status = STATUS['good'] if m['system']['disk'] < 80 else STATUS['warning']
    
    status_text = (
        f"⚡ *МОНИТОРИНГ СИСТЕМЫ*\n"
        f"`(обновлено за 0.1 сек)`\n\n"
        f"🤖 *Боты:* {bot_status} {m['bots']['active']}/{m['bots']['total']}\n"
        f"💻 *CPU:* {m['system']['cpu']:.1f}%\n"
        f"🧠 *RAM:* {m['system']['memory']:.1f}% ({m['system']['memory_used']:.1f}/{m['system']['memory_total']:.1f} GB)\n"
        f"💾 *Диск:* {disk_status} {m['system']['disk']:.1f}% ({m['system']['disk_used']:.1f}/{m['system']['disk_total']:.1f} GB)\n"
        f"🔐 *Redis:* {redis_status} ({m['redis'].get('memory_mb', 0)} MB)\n"
        f"📦 *Бэкапы:* {m['backups']['count']} файлов\n"
        f"🕐 *Аптайм:* {int(m['system']['uptime'] / 3600)}ч\n\n"
        f"⚡ *Выберите действие:*"
    )
    
    keyboard = [
        [InlineKeyboardButton("🤖 Детально о ботах", callback_data='bots_detail')],
        [InlineKeyboardButton("💻 Ресурсы", callback_data='resources')],
        [InlineKeyboardButton("📦 Бэкапы", callback_data='backups')],
        [InlineKeyboardButton("🔐 Redis", callback_data='redis_detail')],
        [InlineKeyboardButton("🔄 Обновить", callback_data='refresh')],
    ]
    
    await update.message.reply_text(
        status_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'refresh':
        # Просто обновляем главное меню
        await start(update, context)
        return
    
    # Получаем свежие метрики
    m = metrics.get_all_metrics()
    
    if query.data == 'bots_detail':
        text = "🤖 *ДЕТАЛЬНЫЙ СТАТУС БОТОВ*\n\n"
        
        # Активные боты
        if m['bots']['active_list']:
            text += "✅ *Работают:*\n"
            for bot in m['bots']['active_list']:
                text += f"   • {bot}\n"
        
        # Неактивные боты
        if m['bots']['inactive']:
            text += "\n❌ *Не работают:*\n"
            for bot in m['bots']['inactive']:
                text += f"   • {bot}\n"
        
        text += f"\n📊 Всего: {m['bots']['active']}/{m['bots']['total']}"
    
    elif query.data == 'resources':
        text = (
            f"💻 *РЕСУРСЫ*\n\n"
            f"⚡ *CPU:* {m['system']['cpu']:.1f}%\n\n"
            f"🧠 *RAM:*\n"
            f"   Использовано: {m['system']['memory_used']:.1f} GB\n"
            f"   Всего: {m['system']['memory_total']:.1f} GB\n"
            f"   Загрузка: {m['system']['memory']:.1f}%\n\n"
            f"💾 *Диск:*\n"
            f"   Использовано: {m['system']['disk_used']:.1f} GB\n"
            f"   Всего: {m['system']['disk_total']:.1f} GB\n"
            f"   Загрузка: {m['system']['disk']:.1f}%\n\n"
            f"🕐 *Аптайм:* {int(m['system']['uptime'] / 3600)}ч {int((m['system']['uptime'] % 3600)/60)}м"
        )
    
    elif query.data == 'backups':
        text = f"📦 *БЭКАПЫ*\n\n"
        if m['backups']['count'] > 0:
            text += f"📊 Всего файлов: {m['backups']['count']}\n"
            text += f"📅 Последний: {m['backups']['latest']}\n"
            text += f"📏 Размер: {m['backups']['latest_size_mb']} MB\n"
            text += f"🕐 Время: {m['backups']['latest_time'][:19].replace('T', ' ')}"
        else:
            text += "❌ Бэкапы не найдены"
    
    elif query.data == 'redis_detail':
        text = f"🔐 *REDIS*\n\n"
        if m['redis']['status'] == 'online':
            text += f"🟢 Статус: работает\n"
            text += f"⚡ Задержка: {m['redis']['latency']}\n"
            text += f"📊 Память: {m['redis']['memory_mb']} MB"
        else:
            text += "🔴 Redis не отвечает"
    
    # Кнопка назад
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back')]]
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    await start(update, context)

def main():
    print("🚀 Запуск быстрого статус-бота @vanxo2030bot...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern='^(?!back$).*'))
    app.add_handler(CallbackQueryHandler(back, pattern='^back$'))
    app.run_polling()

if __name__ == "__main__":
    main()
