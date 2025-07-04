# 🤖 Spina Bot - Бот для заботы о здоровье спины

Автоматизированный Telegram бот-помощник для мониторинга состояния спины и предоставления персональных видео-тренировок.

## 🌟 Основные возможности

### Для пользователей:
- ✅ Ежедневные напоминания об оценке состояния спины
- 📊 Персональная статистика и отслеживание прогресса
- 🎥 Получение видео-тренировок в зависимости от уровня боли
- 📱 Простой интерфейс с кнопками для быстрой оценки

### Для администраторов:
- 🔧 Управление видео-уроками для каждого уровня боли (1-5)
- ⏰ Настройка времени ежедневных напоминаний
- 📈 Просмотр детальной статистики использования
- 👥 Управление пользователями и рассылками

## 🚀 Быстрый старт

Выберите один из способов запуска:

### 🐳 Запуск с Docker (рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/your-repo/spina_bot.git
cd spina_bot

# 2. Создайте .env файл с токеном бота
echo "BOT_TOKEN=your_bot_token_here" > .env

# 3. Запустите с Docker
docker-compose up -d

# 4. Просмотр логов
docker-compose logs -f spina-bot
```

Подробнее в [DOCKER.md](DOCKER.md)

### 🐍 Запуск с Python

#### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 2. Создание бота в Telegram

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте токен вашего бота

#### 3. Настройка переменных окружения

Создайте файл `.env` в корневой папке проекта:

```env
BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///spina_bot.db
```

#### 4. Запуск бота

```bash
python main.py
```

## 📋 Команды бота

### Для всех пользователей:
- `/start` - Регистрация и начало работы с ботом
- `/rate` - Ручная оценка состояния спины
- `/stats` - Личная статистика
- `/stop` - Отключить ежедневные напоминания
- `/resume` - Включить ежедневные напоминания
- `/status` - Проверить статус напоминаний
- `/help` - Справка по использованию

### Для администраторов:
- `/admin` - Открыть панель администратора

## 👨‍💼 Администраторы

В коде заданы два администратора с ID:
- `354786612` (первый администратор)
- `740144550` (второй администратор)

Администраторы могут:
- 🎥 Загружать и управлять видео-уроками
- ⏰ Изменять время ежедневных напоминаний
- 📊 Просматривать статистику всех пользователей
- 👥 Управлять пользователями

## 🎥 Управление видео-уроками

1. Войдите в панель администратора: `/admin`
2. Выберите "🎥 Управление видео-уроками"
3. Выберите уровень боли (1-5)
4. Загрузите видеофайл
5. Добавьте название урока (опционально)
6. Добавьте описание урока (опционально)

Видео-уроки будут автоматически отправляться пользователям в зависимости от их оценки боли.

## ⏰ Настройка напоминаний

По умолчанию напоминания отправляются в 10:00 каждый день. Для изменения:

1. Войдите в панель администратора: `/admin`
2. Выберите "⏰ Настройки времени"
3. Измените время или отключите напоминания

## 📊 База данных

Бот использует SQLite база данных со следующими таблицами:

- `users` - Информация о пользователях
- `user_responses` - История оценок боли
- `video_lessons` - Видео-уроки для разных уровней боли
- `bot_settings` - Настройки бота

## 🔧 Структура проекта

```
spina_bot/
├── main.py              # Основной файл бота
├── database.py          # Модели базы данных
├── user_handlers.py     # Обработчики для пользователей
├── admin_handlers.py    # Обработчики для администраторов
├── requirements.txt     # Зависимости Python
├── Dockerfile          # Docker конфигурация
├── docker-compose.yml  # Docker Compose конфигурация
├── .env.example        # Пример переменных окружения
├── README.md           # Основная документация
├── SETUP.md           # Пошаговая настройка
├── DOCKER.md          # Инструкции по Docker
└── USAGE_EXAMPLES.md  # Примеры использования
```

## 🔍 Логирование

Бот ведет подробные логи работы:
- Регистрация новых пользователей
- Отправка напоминаний
- Ошибки при работе с API Telegram
- Административные действия

## 🛠️ Технические детали

- **Язык**: Python 3.8+
- **Фреймворк**: python-telegram-bot 20.7
- **База данных**: SQLite (SQLAlchemy ORM)
- **Планировщик**: Встроенный в python-telegram-bot

## 📝 Примеры использования

### Пользователь:
1. Отправляет `/start`
2. Получает приветствие и инструкции
3. Оценивает боль от 1 до 5
4. Получает персональный видео-урок
5. Каждый день получает напоминание

### Администратор:
1. Отправляет `/admin`
2. Загружает видео для уровня боли 4
3. Добавляет описание: "Сделайте 3 упражнения 'кошечка' и диафрагмальное дыхание"
4. Устанавливает время напоминаний на 09:00

## 🔒 Безопасность

- Проверка прав администратора для всех административных функций
- Валидация входных данных
- Обработка ошибок и исключений
- Автоматическая деактивация заблокированных пользователей

## 🐛 Решение проблем

### Бот не отвечает
- Проверьте правильность токена в `.env`
- Убедитесь, что бот не заблокирован в Telegram

### Ошибки с базой данных
- Проверьте права на запись в папку с проектом
- Удалите файл `spina_bot.db` для пересоздания

### Не работают напоминания
- Проверьте настройки времени в админ-панели
- Убедитесь, что напоминания включены

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи бота
2. Убедитесь в правильности настроек
3. Перезапустите бота

---

💙 **Берегите свою спину и будьте здоровы!** 