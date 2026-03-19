#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient
import os
import socks  # для прокси, если нужно

async def main():
    print("\n" + "="*50)
    print("📱 АВТОРИЗАЦИЯ TELEGRAM ДЛЯ АНАЛИТИКИ")
    print("="*50)

    api_id = 35315536
    api_hash = "765000bb939887252acff06eca7e117f"
    phone = "+79202280268"

    print(f"\nAPI ID: {api_id}")
    print(f"Phone: {phone}")
    print("-"*50)

    # Пробуем разные настройки подключения
    print("\n🔄 Попытка подключения к Telegram...")
    
    # Вариант 1: Без прокси (стандартное подключение)
    client = TelegramClient('admin_analytics', api_id, api_hash)
    
    try:
        # Пытаемся подключиться
        await client.connect()
        
        if not await client.is_user_authorized():
            print("✅ Подключение установлено, запрашиваю код...")
            
            # Отправляем запрос кода
            await client.send_code_request(phone)
            
            print("\n✅ Код отправлен! Проверьте Telegram на телефоне.")
            print("   (Сообщение от самого Telegram с 5 цифрами)")
            print("-"*50)
            
            code = input("📱 ВВЕДИТЕ КОД ИЗ TELEGRAM: ").strip()
            
            await client.sign_in(phone, code)
            
            print("\n✅ АВТОРИЗАЦИЯ УСПЕШНА!")
            
            me = await client.get_me()
            print(f"Вы вошли как: {me.first_name} (@{me.username})")
            
            # Сохраняем информацию об успехе
            with open("/root/.telegram_auth_success", "w") as f:
                f.write("success")
            
            print("\n📢 Сессия сохранена в файле 'admin_analytics.session'")
            print("\n✅ Теперь админ-бот может работать с аналитикой!")
        else:
            print("✅ Уже авторизован!")
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\n💡 Варианты решения:")
        print("   1. Проверьте интернет-соединение сервера")
        print("   2. Попробуйте позже (возможно временные проблемы Telegram)")
        print("   3. Если вы в РФ, возможно нужен VPN/прокси")
        print("\n   Для установки прокси выполните:")
        print("   pip install pysocks")
        print("   и раскомментируйте соответствующий код в скрипте")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
