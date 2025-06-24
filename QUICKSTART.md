# 🚀 Быстрый старт Spina Bot

## 🐳 Docker (рекомендуется)

### 1. Подготовка
```bash
# Клонируйте репозиторий
git clone <repository-url>
cd spina_bot

# Создайте необходимые директории
mkdir -p data logs backups

# Создайте .env файл
cp .env.example .env
```

### 2. Настройка переменных окружения
Отредактируйте `.env`:
```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite:///app/data/spina_bot.db
```

### 3. Запуск бота
```bash
# Сборка и запуск
docker-compose up --build -d

# Проверка логов
docker-compose logs -f spina-bot
```

### 🔧 Исправление ошибки "unable to open database file"

Если возникает ошибка с базой данных:

```bash
# 1. Остановите контейнер
docker-compose down

# 2. Убедитесь что директории созданы
mkdir -p data logs

# 3. Пересоберите контейнер полностью
docker-compose build --no-cache

# 4. Запустите заново
docker-compose up -d

# 5. Проверьте логи
docker-compose logs -f spina-bot
```

### 🔍 Проверка работы

После запуска вы должны увидеть:
```
spina-bot  | ✅ BOT_TOKEN найден
spina-bot  | ✅ Директория для базы данных готова
spina-bot  | 🗄️ Инициализация базы данных...
spina-bot  | ✅ База данных инициализирована
spina-bot  | 🤖 Запуск бота...
spina-bot  | Бот готов к работе!
```

---

## 🐍 Python (разработка)

### 1. Подготовка окружения
```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка
```bash
# Создайте .env файл
cp .env.example .env

# Отредактируйте .env файл
# BOT_TOKEN=your_telegram_bot_token_here
# DATABASE_URL=sqlite:///spina_bot.db
```

### 3. Запуск
```bash
# Создайте директории
mkdir -p data logs

# Запустите бота
python main.py
```

---

## 📱 Первое использование

1. **Найдите своего бота** в Telegram
2. **Отправьте** `/start`
3. **Для админов:** используйте `/admin` для управления

## 🛟 Помощь

- 📖 [Полная документация](README.md)
- 🐛 [Устранение проблем](TROUBLESHOOTING.md)
- 🐳 [Docker руководство](DOCKER.md)

## 📋 Первоначальная настройка

1. **Получите токен бота** у [@BotFather](https://t.me/botfather)
2. **Настройте администраторов** - замените ID в `admin_handlers.py`
3. **Загрузите аудиосообщения** через `/admin` → "🎵 Управление аудио"
4. **Настройте время напоминаний** через `/admin` → "⏰ Настройки времени"

## 🎯 Команды для пользователей

- `/start` - Начать работу
- `/rate` - Оценить боль (1-5)
- `/stats` - Моя статистика
- `/stop` - Отключить напоминания
- `/resume` - Включить напоминания
- `/status` - Статус напоминаний

## 🔧 Команды для администраторов

- `/admin` - Панель управления

---

📖 **Подробная документация:** [README.md](README.md) | [SETUP.md](SETUP.md) | [DOCKER.md](DOCKER.md) 