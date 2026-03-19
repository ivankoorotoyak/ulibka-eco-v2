#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient
import os

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

    # Создаём клиента
    client = TelegramClient('admin_analytics', api_id, api_hash)
    
    try:
        # Явно подключаемся
        print("\n🔄 Подключаюсь к Telegram...")
        await client.connect()
        
        if not await client.is_user_authorized():
            print("✅ Подключено! Запрашиваю код...")
            
            # Отправляем запрос кода
            await client.send_code_request(phone)
            
            print("\n✅ Код отправлен! Проверьте Telegram на телефоне.")
            print("   Ищите сообщение от 'Telegram' с 5 цифрами")
            print("-"*50)
            
            code = input("📱 ВВЕДИТЕ КОД ИЗ TELEGRAM: ").strip()
            
            try:
                await client.sign_in(phone, code)
                print("\n✅ АВТОРИЗАЦИЯ УСПЕШНА!")
                
                me = await client.get_me()
                print(f"Вы вошли как: {me.first_name} (@{me.username})")
                
                # Проверяем доступ к каналам
                print("\n📢 Проверяю доступ к каналам...")
                channels = [
                    "@ulybka_plus_24_7",
                    "@ulybka_plus_fact",
                    "@ulybka_plus_kids",
                    "@ulybka_plus_humor",
                    "@ulybka_plus_philo",
                    "@ulybka_plus_dreams",
                    "@ulybka_plus_news",
                    "@ulybka_plus_sos"
                ]
                
                for channel in channels:
                    try:
                        entity = await client.get_entity(channel)
                        print(f"  ✅ {channel}: доступен")
                    except Exception as e:
                        print(f"  ❌ {channel}: {str(e)[:50]}")
                
                # Сохраняем информацию об успехе
                with open("/root/.telegram_auth_success", "w") as f:
                    f.write("success")
                
                print("\n📢 Сессия сохранена в файле 'admin_analytics.session'")
                print("\n✅ АНАЛИТИКА ГОТОВА К РАБОТЕ!")
                
            except Exception as e:
                print(f"\n❌ Ошибка при вводе кода: {e}")
                print("💡 Попробуйте ещё раз, внимательно введите код")
        else:
            print("✅ Уже авторизован! Можно работать.")
            
            # Показываем информацию о себе
            me = await client.get_me()
            print(f"Вы вошли как: {me.first_name} (@{me.username})")
            
    except Exception as e:
        print(f"\n❌ Ошибка подключения: {e}")
        print("\n💡 Возможные решения:")
        print("   1. Проверьте интернет-соединение сервера")
        print("   2. Попробуйте позже (возможно временные проблемы)")
        print("   3. Если вы в РФ, может потребоваться VPN")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
