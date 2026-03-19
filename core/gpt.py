#!/usr/bin/env python3
import os
import httpx
from typing import Optional

class YandexGPT:
    def __init__(self, folder_id: str = None, api_key: str = None):
        self.folder_id = folder_id or os.getenv("YANDEX_FOLDER_ID", "b1gjatvnea5nfs88fncv")
        self.api_key = api_key or os.getenv("YANDEXGPT_API_KEY")
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_response(self, 
                               prompt: str, 
                               system_prompt: str = "Ты - полезный ассистент стоматологической клиники",
                               temperature: float = 0.6,
                               max_tokens: int = 1000) -> Optional[str]:
        """Генерация ответа через YandexGPT"""
        
        if not self.api_key:
            print("⚠️ YandexGPT API ключ не настроен")
            return None
        
        body = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": max_tokens
            },
            "messages": [
                {
                    "role": "system",
                    "text": system_prompt
                },
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                return result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
            except Exception as e:
                print(f"❌ Ошибка YandexGPT: {e}")
                return None
