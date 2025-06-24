#!/bin/bash
set -e

echo "🚀 Запуск Spina Bot..."

# Проверяем наличие токена
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Ошибка: BOT_TOKEN не установлен"
    exit 1
fi

echo "✅ BOT_TOKEN найден"

# Проверяем/создаем директорию для базы данных
DB_DIR="/app/data"
if [ ! -d "$DB_DIR" ]; then
    echo "📁 Создание директории для базы данных: $DB_DIR"
    mkdir -p "$DB_DIR"
fi

echo "✅ Директория для базы данных готова"

# Инициализируем базу данных
echo "🗄️ Инициализация базы данных..."
python init_db.py

if [ $? -eq 0 ]; then
    echo "✅ База данных инициализирована"
else
    echo "❌ Ошибка инициализации базы данных"
    exit 1
fi

# Запускаем бота
echo "🤖 Запуск бота..."
exec python main.py 