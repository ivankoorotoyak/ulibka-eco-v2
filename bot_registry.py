#!/usr/bin/env python3
"""
Реестр всех ботов экосистемы
Версия: 6.2
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class BotStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    DISABLED = "disabled"


@dataclass
class BotInfo:
    name: str
    username: str
    token_key: str
    status: BotStatus
    description: str
    service_name: str


# РЕЕСТР ВСЕХ БОТОВ (15)
BOT_REGISTRY: Dict[str, BotInfo] = {
    # Основные боты (12)
    "prof_bot": BotInfo("prof_bot", "@profmedicalbot", "PROF_BOT_TOKEN", BotStatus.ACTIVE, "Научный помощник", "prof_bot.service"),
    "dentai_bot": BotInfo("dentai_bot", "@dentai_smile_bot", "DENTAI_BOT_TOKEN", BotStatus.ACTIVE, "Стоматологический помощник", "dentai_bot.service"),
    "dentai_help_bot": BotInfo("dentai_help_bot", "@dentai_help_bot", "DENTAI_HELP_BOT_TOKEN", BotStatus.ACTIVE, "Справочник стоматологии", "dentai_help_bot.service"),
    "dream_bot": BotInfo("dream_bot", "@dream_smilebot", "DREAM_BOT_TOKEN", BotStatus.ACTIVE, "Анализ сновидений", "dream_bot.service"),
    "inclusive_bot": BotInfo("inclusive_bot", "@Ulibka_inclusive_bot", "INCLUSIVE_BOT_TOKEN", BotStatus.ACTIVE, "Инклюзивность", "inclusive_bot.service"),
    "karta_bot": BotInfo("karta_bot", "@vanxo2030bot", "KARTA_BOT_TOKEN", BotStatus.ACTIVE, "Карта услуг", "karta_bot.service"),
    "admin_bot": BotInfo("admin_bot", "@vanxoadmin_bot", "ADMIN_BOT_TOKEN", BotStatus.ACTIVE, "Администрирование", "admin_bot.service"),
    "clean_bot": BotInfo("clean_bot", "@hygiene_ulibkabot", "CLEAN_BOT_TOKEN", BotStatus.ACTIVE, "Гигиена", "clean_bot.service"),
    "joke_bot": BotInfo("joke_bot", "@Ulibka_jokeBot", "JOKE_BOT_TOKEN", BotStatus.ACTIVE, "Юмор", "joke_bot.service"),
    "implant_bot": BotInfo("implant_bot", "@Stomvrn_bot", "IMPLANT_BOT_TOKEN", BotStatus.ACTIVE, "Импланты", "implant_bot.service"),
    "kid_bot": BotInfo("kid_bot", "@Ulibka_kidBot", "KID_BOT_TOKEN", BotStatus.ACTIVE, "Детский", "kid_bot.service"),
    "philo_bot": BotInfo("philo_bot", "@Ulibka_philoBot", "PHILO_BOT_TOKEN", BotStatus.ACTIVE, "Философия", "philo_bot.service"),
    
    # Новые боты (3)
    "family_bot": BotInfo("family_bot", "@family_smilebot", "FAMILY_BOT_TOKEN", BotStatus.ACTIVE, "Семейный контент", "family_bot.service"),
    "ortho_bot": BotInfo("ortho_bot", "@ortho_smilebot", "ORTHO_BOT_TOKEN", BotStatus.ACTIVE, "Ортодонтия", "ortho_bot.service"),
    "shop_bot": BotInfo("shop_bot", "@shop_ulibkabot", "SHOP_BOT_TOKEN", BotStatus.ACTIVE, "Магазин", "shop_bot.service"),
}


def get_bot_info(bot_name: str) -> Optional[BotInfo]:
    return BOT_REGISTRY.get(bot_name)


def get_all_active_bots() -> List[BotInfo]:
    return [b for b in BOT_REGISTRY.values() if b.status == BotStatus.ACTIVE]


def get_pending_bots() -> List[BotInfo]:
    return [b for b in BOT_REGISTRY.values() if b.status == BotStatus.PENDING]


def get_token_key(bot_name: str) -> Optional[str]:
    info = get_bot_info(bot_name)
    return info.token_key if info else None


if __name__ == "__main__":
    print("=== БОТ РЕЕСТР V6.2 ===\n")
    print(f"Всего ботов: {len(BOT_REGISTRY)}")
    print(f"Активных: {len(get_all_active_bots())}")
    print(f"Ожидают токены: {len(get_pending_bots())}")
    print("\nАктивные боты:")
    for bot in get_all_active_bots():
        print(f"  ✅ {bot.name} ({bot.username})")
