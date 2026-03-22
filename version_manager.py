#!/usr/bin/env python3
import json, os, shutil, datetime, glob

CONFIG_DIR = "/opt/smile_bots"
BACKUP_DIR = "/opt/smile_bots/backups"
VERSIONS_FILE = "/opt/smile_bots/versions.json"

def init_versions():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.exists(VERSIONS_FILE):
        with open(VERSIONS_FILE, 'w') as f:
            json.dump({"current": {}, "history": []}, f, indent=2)

def create_version():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    version_dir = f"{BACKUP_DIR}/v{timestamp}"
    os.makedirs(version_dir, exist_ok=True)
    for bot_file in glob.glob(f"{CONFIG_DIR}/*_bot.py"):
        shutil.copy2(bot_file, version_dir)
    if os.path.exists(f"{CONFIG_DIR}/ecosystem_state.json"):
        shutil.copy2(f"{CONFIG_DIR}/ecosystem_state.json", version_dir)
    with open(VERSIONS_FILE, 'r') as f:
        versions = json.load(f)
    version_info = {"version": timestamp, "date": datetime.datetime.now().isoformat(), "files": len(os.listdir(version_dir)), "path": version_dir}
    versions["current"] = version_info
    versions["history"].insert(0, version_info)
    versions["history"] = versions["history"][:30]
    with open(VERSIONS_FILE, 'w') as f:
        json.dump(versions, f, indent=2)
    return version_info

def rollback(version=None):
    with open(VERSIONS_FILE, 'r') as f:
        versions = json.load(f)
    if version is None and versions["history"]:
        version = versions["history"][1] if len(versions["history"]) > 1 else versions["current"]
    if version:
        for bot_file in glob.glob(f"{version['path']}/*_bot.py"):
            shutil.copy2(bot_file, CONFIG_DIR)
        print(f"✅ Откат к версии {version['version']} выполнен")
        return True
    print("❌ Нет доступных версий")
    return False

if __name__ == "__main__":
    init_versions()
    import sys
    if "--create" in sys.argv:
        result = create_version()
        print(f"✅ Создана версия: {result['version']}")
    elif "--rollback" in sys.argv:
        rollback()
    else:
        with open(VERSIONS_FILE, 'r') as f:
            print(json.dumps(json.load(f), indent=2))
