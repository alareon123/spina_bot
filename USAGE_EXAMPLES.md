# 📚 Примеры использования Spina Bot

## 👤 Для обычных пользователей

### Первый запуск
```
Пользователь: /start
Бот: Привет, Иван! 👋
     Я бот-помощник для заботы о здоровье вашей спины! 🌟
     ...
     Давайте начнем! Как ваша спина сегодня?
     [Кнопки: 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣]

Пользователь: [нажимает 3️⃣]
Бот: Спасибо за оценку! Уровень боли: 3
     Сделайте 3 упражнения "кошечка" и диафрагмальное дыхание
     [отправляет видео-урок с упражнениями]
```

### Ручная оценка боли
```
Пользователь: /rate
Бот: 🩺 Оценка состояния спины
     Как ваша спина прямо сейчас?
     Оцените уровень боли от 1 до 5:
     [Кнопки: 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣]
```

### Просмотр статистики
```
Пользователь: /stats
Бот: 📊 Ваша статистика
     📅 Дата регистрации: 15.06.2024
     💬 Всего оценок: 25
     📈 Средний уровень боли: 2.8
     🕐 Последняя оценка: 24.06.2024 10:30
     🎯 Последний уровень: 3
     
     📋 Распределение по уровням:
     Уровень 1: 5 раз (20.0%)
     Уровень 2: 8 раз (32.0%)
     Уровень 3: 7 раз (28.0%)
     Уровень 4: 4 раз (16.0%)
     Уровень 5: 1 раз (4.0%)
```

## 👨‍💼 Для администраторов

### Вход в админ-панель
```
Администратор: /admin
Бот: 🔧 Панель администратора
     
     Выберите действие:
     [🎥 Управление видео-уроками] [⏰ Настройки времени]
     [📊 Статистика] [👥 Управление пользователями]
```

### Загрузка видео-урока
```
Администратор: [выбирает уровень боли 4]
Бот: Отправьте видео-урок для уровня боли 4:

Администратор: [отправляет видеофайл]
Бот: Теперь отправьте название для этого видео-урока:

Администратор: Упражнения при сильной боли

Бот: Теперь отправьте описание для этого видео-урока:

Администратор: При сильной боли рекомендую отдых и дыхательные техники
Бот: ✅ Видео-урок для уровня боли 4 успешно сохранен!
```

💙 **Используйте бота регулярно для лучших результатов!** 