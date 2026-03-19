#!/usr/bin/env python3
"""
Инклюзивный голосовой бот для людей с ограниченными возможностями
- Полностью голосовое управление
- Крупный текст для слабовидящих
- Простой интерфейс
"""

import os
import sys
import tempfile
import asyncio
import logging
from datetime import datetime
sys.path.append('/root/ulibka-eco-v2')

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from core.voice import YandexSpeechKit
from core.gpt import YandexGPT

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.environ.get('INCLUSIVE_BOT_TOKEN', '')
ADMIN_ID = os.environ.get('ADMIN_ID', '8052686185')
CLINIC_PHONE = "+7 (920) 228-02-68"

# Инициализация сервисов
speechkit = YandexSpeechKit()
gpt = YandexGPT()

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def make_large_text(text: str) -> str:
    """Делает текст крупным для слабовидящих"""
    return f"🔹 {text}"

# ========== ОСНОВНЫЕ ОБРАБОТЧИКИ ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение с голосовым приветствием"""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} запустил инклюзивного бота")
    
    welcome_text = (
        "👋 Здравствуйте! Я голосовой помощник стоматологии 'Улыбка+'.\n\n"
        "🎤 **Я создан специально для людей, которым трудно печатать или видеть экран.**\n\n"
        "📢 **Как пользоваться:**\n"
        "• Отправьте **голосовое сообщение** с вашим вопросом\n"
        "• Я отвечу **голосом** и продублирую **крупным текстом**\n"
        "• Просто говорите, что вас интересует!\n\n"
        f"📞 Если бот не работает, позвоните: {CLINIC_PHONE}"
    )
    
    await update.message.reply_text(
        make_large_text(welcome_text),
        parse_mode='Markdown'
    )
    
    # Отправляем голосовое приветствие
    try:
        voice_greeting = "Здравствуйте! Я голосовой помощник стоматологии Улыбка плюс. Отправьте голосовое сообщение с вашим вопросом."
        voice_data = await speechkit.text_to_speech(voice_greeting, voice="alena", emotion="good")
        
        if voice_data:
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
                f.write(voice_data)
                f.flush()
                with open(f.name, 'rb') as audio_file:
                    await update.message.reply_voice(
                        voice=audio_file,
                        caption="🎤 Голосовое приветствие"
                    )
                os.unlink(f.name)
    except Exception as e:
        logger.error(f"Ошибка голосового приветствия: {e}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений"""
    user = update.effective_user
    logger.info(f"Получено голосовое сообщение от {user.id}")
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    processing_msg = await update.message.reply_text("🎧 Обрабатываю ваше голосовое сообщение...")
    
    try:
        # Скачиваем голосовое сообщение
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        
        # Распознаём речь в текст
        recognized_text = await speechkit.speech_to_text(bytes(voice_bytes))
        
        if not recognized_text:
            await processing_msg.edit_text("❌ Не удалось распознать речь. Попробуйте ещё раз.")
            return
        
        # Показываем распознанный текст
        await processing_msg.edit_text(
            f"📝 **Я распознал:**\n{recognized_text}\n\n⏳ Формирую ответ..."
        )
        
        # Формируем системный промпт
        system_prompt = (
            "Ты - голосовой помощник стоматологической клиники 'Улыбка+'. "
            "Твои пользователи - пожилые люди, люди с ограниченным зрением. "
            "Отвечай кратко, чётко, доброжелательно. Используй простые слова. "
            f"Если нужна запись - скажи позвонить по телефону {CLINIC_PHONE}."
        )
        
        # Получаем ответ от YandexGPT
        response_text = await gpt.generate_response(recognized_text, system_prompt=system_prompt)
        
        if not response_text:
            response_text = f"Извините, я временно не могу ответить. Пожалуйста, позвоните в клинику: {CLINIC_PHONE}"
        
        # Отправляем голосовой ответ
        voice_response = await speechkit.text_to_speech(response_text, voice="alena", emotion="good")
        
        if voice_response:
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
                f.write(voice_response)
                f.flush()
                with open(f.name, 'rb') as audio_file:
                    await update.message.reply_voice(voice=audio_file)
                os.unlink(f.name)
        
        # Отправляем текстовый ответ крупным шрифтом
        await update.message.reply_text(
            f"📢 **Ответ:**\n\n{make_large_text(response_text)}"
        )
        
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке голоса: {e}")
        await processing_msg.edit_text(
            f"❌ Произошла ошибка. Пожалуйста, позвоните: {CLINIC_PHONE}"
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    text = update.message.text
    logger.info(f"Получено текстовое сообщение: {text[:50]}...")
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        system_prompt = "Ты - голосовой помощник стоматологии 'Улыбка+'. Отвечай кратко."
        response_text = await gpt.generate_response(text, system_prompt=system_prompt)
        
        if not response_text:
            response_text = f"Позвоните в клинику: {CLINIC_PHONE}"
        
        await update.message.reply_text(f"📢 {make_large_text(response_text)}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки текста: {e}")
        await update.message.reply_text(f"❌ Ошибка. Звоните: {CLINIC_PHONE}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    help_text = (
        "📋 **Как пользоваться ботом:**\n\n"
        "1️⃣ **Голосом**: просто отправьте голосовое сообщение\n"
        "2️⃣ **Текстом**: напишите вопрос\n"
        f"3️⃣ **Если не работает**: позвоните {CLINIC_PHONE}\n\n"
        "Бот адаптирован для слабовидящих и пожилых людей."
    )
    await update.message.reply_text(make_large_text(help_text))

# ========== ЗАПУСК ==========

def main():
    if not BOT_TOKEN:
        print("❌ Ошибка: INCLUSIVE_BOT_TOKEN не задан")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("🤖 Инклюзивный бот запущен")
    print("✅ Инклюзивный бот запущен. Ожидание сообщений...")
    
    app.run_polling()

if __name__ == "__main__":
    main()
