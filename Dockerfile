# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Создаем директорию для базы данных
RUN mkdir -p /app/data

# Устанавливаем переменную окружения для базы данных
ENV DATABASE_URL=sqlite:///data/spina_bot.db

# Создаем пользователя без root прав
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Открываем порт (не обязательно для Telegram бота, но хорошая практика)
EXPOSE 8000

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('/app/data/spina_bot.db').execute('SELECT 1')" || exit 1

# Команда запуска
CMD ["python", "main.py"] 