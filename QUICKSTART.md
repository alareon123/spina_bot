# ⚡ Быстрый запуск Spina Bot

## 🐳 С Docker (рекомендуется)

```bash
# 1. Скачайте проект
git clone https://github.com/your-repo/spina_bot.git
cd spina_bot

# 2. Настройте токен бота
echo "BOT_TOKEN=your_bot_token_here" > .env

# 3. Запустите
docker-compose up -d

# 4. Проверьте логи
docker-compose logs -f spina-bot
```

## 🐍 С Python

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Настройте токен в .env
echo "BOT_TOKEN=your_bot_token_here" > .env

# 3. Запустите
python main.py
```

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