#!/usr/bin/env python3
import os
import httpx
import base64
from pydub import AudioSegment
from io import BytesIO

class YandexSpeechKit:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SPEECHKIT_API_KEY")
        self.stt_url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        self.tts_url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    
    async def speech_to_text(self, voice_bytes: bytes) -> str:
        """Распознавание голоса в текст"""
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "audio/ogg"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.stt_url,
                    headers=headers,
                    content=voice_bytes,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                return result.get("result", "")
            except Exception as e:
                print(f"❌ Ошибка STT: {e}")
                return ""
    
    async def text_to_speech(self, text: str, voice: str = "oksana", emotion: str = "neutral") -> bytes:
        """Синтез речи из текста"""
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
        }
        
        data = {
            "text": text,
            "voice": voice,
            "emotion": emotion,
            "format": "oggopus",
            "sampleRateHertz": 48000
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.tts_url,
                    headers=headers,
                    data=data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.content
            except Exception as e:
                print(f"❌ Ошибка TTS: {e}")
                return b""
