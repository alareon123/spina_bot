#!/usr/bin/env python3
"""
Скрипт инициализации базы данных для Spina Bot
"""

import os
import sys
from database import create_tables, init_default_settings

def main():
    """Инициализация базы данных"""
    try:
        print("🗄️ Инициализация базы данных...")
        
        # Создаем таблицы
        create_tables()
        print("✅ Таблицы созданы")
        
        # Инициализируем настройки по умолчанию
        init_default_settings()
        print("✅ Настройки по умолчанию установлены")
        
        print("🎉 База данных успешно инициализирована!")
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 