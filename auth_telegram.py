#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient
import os
import sys

async def main():
    print("\n" + "="*50)
    print("📱 АВТОРИЗАЦИЯ TELEGRAM ДЛЯ АНАЛИТИКИ")
    print("="*50)
    
    # Данные из my.telegram.org
    api_id = 35315536
    api_hash = "765000bb939887252acff06eca7e117f"
    phone = "+79202280268"
    
    print(f"\nAPI ID: {api_id}")
    print(f"Phone: {phone}")
    print("-"*50)
    
    # Создаём клиент
    client = TelegramClient('admin_analytics', api_id, api_hash)
    
    try:
        # Запускаем авторизацию
        await client.start(phone=phone)
        print("\n✅ АВТОРИЗАЦИЯ УСПЕШНА!")
        
        # Получаем информацию о себе
        me = await client.get_me()
        print(f"Вы вошли как: {me.first_name} (@{me.username})")
        
        # Сохраняем информацию об успехе
        with open("/root/.telegram_auth_success", "w") as f:
            f.write("success")
        
        print("\n📢 Сессия сохранена в файле 'admin_analytics.session'")
        print("\n✅ Теперь админ-бот может работать с аналитикой!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
