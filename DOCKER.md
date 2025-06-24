# 🐳 Запуск Spina Bot с Docker

## 🚀 Быстрый старт

### 1. Подготовка

Убедитесь, что у вас установлены:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Настройка переменных окружения

Создайте файл `.env` с вашим токеном бота:
```env
BOT_TOKEN=your_bot_token_here
```

### 3. Запуск бота

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f spina-bot

# Остановка
docker-compose down
```

## 📋 Команды Docker Compose

### Основные команды

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Запуск с пересборкой образа
docker-compose up --build -d

# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs spina-bot

# Просмотр логов в реальном времени
docker-compose logs -f spina-bot

# Остановка сервисов
docker-compose stop

# Остановка и удаление контейнеров
docker-compose down

# Остановка с удалением volumes
docker-compose down -v
```

### Управление данными

```bash
# Создание резервной копии базы данных
docker-compose --profile backup run backup

# Просмотр содержимого volume с данными
docker run --rm -v spina_bot_data:/data alpine ls -la /data
```

### Мониторинг

```bash
# Запуск с мониторингом логов (Dozzle)
docker-compose --profile monitoring up -d

# Dozzle будет доступен по адресу http://localhost:8080
```

## 🗂️ Структура директорий

```
spina_bot/
├── data/                 # База данных (persistent volume)
├── logs/                 # Логи бота (опционально)
├── backups/             # Резервные копии
├── docker-compose.yml   # Конфигурация Docker Compose
├── Dockerfile          # Инструкции сборки образа
└── .env               # Переменные окружения
```

## 🔧 Конфигурация

### Переменные окружения

```env
# Обязательные
BOT_TOKEN=your_telegram_bot_token

# Опциональные
DATABASE_URL=sqlite:///data/spina_bot.db
LOG_LEVEL=INFO
```

### Volumes

- `./data:/app/data` - База данных SQLite
- `./logs:/app/logs` - Логи приложения (опционально)

### Порты

- `8080:8080` - Dozzle (просмотр логов) - только с профилем `monitoring`

## 📊 Мониторинг

### Просмотр логов через Dozzle

1. Запустите с профилем мониторинга:
```bash
docker-compose --profile monitoring up -d
```

2. Откройте http://localhost:8080 в браузере

3. Выберите контейнер `spina-bot` для просмотра логов

### Health Check

Docker автоматически проверяет здоровье контейнера каждые 30 секунд:

```bash
# Проверка статуса health check
docker inspect spina-bot --format='{{.State.Health.Status}}'
```

## 💾 Резервное копирование

### Автоматическое резервное копирование

Создайте cron задачу для регулярного бэкапа:

```bash
# Редактируем crontab
crontab -e

# Добавляем строку для ежедневного бэкапа в 3:00
0 3 * * * cd /path/to/spina_bot && docker-compose --profile backup run backup
```

### Ручное резервное копирование

```bash
# Создание резервной копии
docker-compose --profile backup run backup

# Просмотр созданных резервных копий
ls -la backups/
```

### Восстановление из резервной копии

```bash
# Остановка бота
docker-compose stop spina-bot

# Восстановление базы данных
cp backups/spina_bot_backup_YYYYMMDD_HHMMSS.db data/spina_bot.db

# Запуск бота
docker-compose start spina-bot
```

## 🔄 Обновление

### Обновление бота

```bash
# Получение нового кода
git pull

# Пересборка и перезапуск
docker-compose up --build -d

# Проверка логов
docker-compose logs -f spina-bot
```

## 🛠️ Разработка

### Разработка с Docker

```bash
# Запуск в development режиме с монтированием кода
docker-compose -f docker-compose.dev.yml up

# Запуск интерактивной оболочки
docker-compose exec spina-bot bash
```

### Отладка

```bash
# Просмотр подробных логов
docker-compose logs --details spina-bot

# Подключение к контейнеру
docker-compose exec spina-bot sh

# Проверка переменных окружения
docker-compose exec spina-bot env
```

## 🔒 Безопасность

### Рекомендации

1. **Никогда не коммитьте `.env` файл в Git**
2. **Используйте Docker secrets в продакшене**
3. **Регулярно обновляйте базовые образы**
4. **Ограничивайте ресурсы контейнера**

### Пример с Docker secrets

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  spina-bot:
    image: spina-bot:latest
    secrets:
      - bot_token
    environment:
      - BOT_TOKEN_FILE=/run/secrets/bot_token

secrets:
  bot_token:
    file: ./bot_token.txt
```

## 🐛 Устранение проблем

### Частые проблемы

**Контейнер не запускается:**
```bash
# Проверка логов
docker-compose logs spina-bot

# Проверка статуса
docker-compose ps
```

**База данных не сохраняется:**
```bash
# Проверка volumes
docker volume ls
docker volume inspect spina_bot_data
```

**Нет доступа к файлам:**
```bash
# Проверка прав доступа
ls -la data/
sudo chown -R 1000:1000 data/
```

### Очистка

```bash
# Удаление всех контейнеров и образов
docker-compose down --rmi all --volumes --remove-orphans

# Очистка всех Docker данных
docker system prune -a --volumes
```

---

🐳 **Удачного использования Docker!** 