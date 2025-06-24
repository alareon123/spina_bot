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

# Создаем пользователя без root прав
RUN adduser --disabled-password --gecos '' appuser

# Создаем директорию для базы данных и устанавливаем права
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Устанавливаем переменную окружения для базы данных
ENV DATABASE_URL=sqlite:///app/data/spina_bot.db

# Переключаемся на пользователя appuser
USER appuser

# Открываем порт (не обязательно для Telegram бота, но хорошая практика)
EXPOSE 8000

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('/app/data') else 1)" || exit 1

# Команда запуска
CMD ["python", "main.py"] 