#!/usr/bin/env python3
"""
Скрипт для управления всеми компонентами EcoEats
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(text):
    """Вывести заголовок"""
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}\n")

def run_command(cmd, description):
    """Выполнить команду"""
    print(f"🚀 {description}")
    print(f"   Команда: {cmd}\n")
    subprocess.run(cmd, shell=True)

def main():
    print_header("🌱 EcoEats - Control Panel")
    
    print("Доступные команды:\n")
    print("1. bot      - Запустить Telegram бота")
    print("2. api      - Запустить REST API")
    print("3. both     - Запустить оба сервиса")
    print("4. test     - Протестировать БД")
    print("5. clean    - Очистить БД\n")
    
    if len(sys.argv) < 2:
        command = input("Выберите команду (1-5): ").strip()
    else:
        command = sys.argv[1]
    
    if command in ["1", "bot"]:
        run_command("python bot_with_db.py", "Запуск Telegram бота")
    
    elif command in ["2", "api"]:
        run_command("python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload", 
                   "Запуск REST API (http://localhost:8000/docs)")
    
    elif command in ["3", "both"]:
        print_header("Запуск обоих сервисов")
        print("⚠️  Откройте два терминала и запустите:\n")
        print("Терминал 1:")
        print("  python bot_with_db.py\n")
        print("Терминал 2:")
        print("  python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload\n")
        input("Нажмите Enter когда готовы...")
    
    elif command in ["4", "test"]:
        run_command("python test_db.py", "Тестирование БД")
    
    elif command in ["5", "clean"]:
        if os.path.exists("ecoeats.db"):
            os.remove("ecoeats.db")
            print("✅ БД удалена")
        else:
            print("❌ БД не найдена")
    
    else:
        print("❌ Неизвестная команда")

if __name__ == "__main__":
    main()
