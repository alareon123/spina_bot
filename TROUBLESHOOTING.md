# 🛠️ Устранение проблем Spina Bot

## 🚨 Ошибка "unable to open database file" в Docker

Эта ошибка возникает из-за проблем с правами доступа к файлу базы данных в Docker контейнере.

### 🔧 Быстрое решение

```bash
# 1. Остановите контейнер
docker-compose down

# 2. Создайте необходимые директории
mkdir -p data logs

# 3. Установите права (Linux/Mac)
sudo chown -R 1000:1000 data logs

# 4. Пересоберите и запустите
docker-compose build --no-cache
docker-compose up -d

# 5. Проверьте логи
docker-compose logs -f spina-bot
```

### 🐧 Для Linux/Mac

```bash
# Убедитесь что директории имеют правильные права
ls -la data/ logs/

# Если нужно, исправьте права
sudo chown -R $(id -u):$(id -g) data logs
chmod -R 755 data logs
```

### 🪟 Для Windows

В PowerShell:
```powershell
# Создайте директории
New-Item -ItemType Directory -Force -Path data, logs

# Перезапустите контейнер
docker-compose down
docker-compose up --build -d
```

### 🔍 Диагностика

```bash
# Проверьте статус контейнера
docker-compose ps

# Проверьте логи
docker-compose logs spina-bot

# Проверьте файловую систему внутри контейнера
docker-compose exec spina-bot ls -la /app/data

# Проверьте переменные окружения
docker-compose exec spina-bot env | grep DATABASE_URL
```

## 🐛 Другие частые проблемы

### Бот не отвечает

```bash
# Проверьте токен
docker-compose exec spina-bot env | grep BOT_TOKEN

# Проверьте интернет соединение
docker-compose exec spina-bot ping telegram.org
```

### Контейнер падает при старте

```bash
# Посмотрите подробные логи
docker-compose logs --details spina-bot

# Запустите в интерактивном режиме для отладки
docker-compose run --rm spina-bot bash
```

### Health check не проходит

```bash
# Проверьте health check вручную
docker inspect spina-bot --format='{{.State.Health.Status}}'

# Запустите health check команду вручную
docker-compose exec spina-bot python -c "import os; print('OK' if os.path.exists('/app/data') else 'FAIL')"
```

## 🔄 Полная переустановка

Если ничего не помогает:

```bash
# 1. Остановите и удалите все
docker-compose down -v
docker system prune -f

# 2. Удалите старые данные (ОСТОРОЖНО!)
rm -rf data/* logs/*

# 3. Пересоздайте с нуля
mkdir -p data logs
docker-compose build --no-cache
docker-compose up -d
```

## 📞 Получение помощи

Если проблема не решается:

1. **Соберите информацию:**
   ```bash
   docker-compose logs spina-bot > bot_logs.txt
   docker inspect spina-bot > container_info.txt
   ```

2. **Проверьте окружение:**
   ```bash
   echo "OS: $(uname -a)"
   echo "Docker: $(docker --version)"
   echo "Docker Compose: $(docker-compose --version)"
   ```

3. **Создайте issue** с собранной информацией

---

💡 **Совет:** Большинство проблем решается пересборкой контейнера с очисткой кеша. 