# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import logging
from datetime import time
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from database import create_tables, init_default_settings, SessionLocal, BotSettings
from user_handlers import start, help_command, rate_pain, handle_pain_rating, user_stats, send_daily_reminder, stop_reminders, resume_reminders, reminder_status
from admin_handlers import (
    admin_panel, handle_admin_callback, receive_audio, receive_text_description, 
    cancel_admin_conversation, WAITING_AUDIO, WAITING_TEXT, is_admin
)

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SpinaBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        if not self.token:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")
        
        # Создаем приложение
        self.application = Application.builder().token(self.token).build()
        
        # Добавляем ссылку на бота в контекст приложения для обновления планировщика
        self.application.spina_bot = self
        
        # Настраиваем обработчики
        self.setup_handlers()
        
        # Настраиваем планировщик
        self.setup_scheduler()
    
    def setup_handlers(self):
        """Настройка всех обработчиков сообщений"""
        
        # Обработчики команд для пользователей
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("rate", rate_pain))
        self.application.add_handler(CommandHandler("stats", user_stats))
        self.application.add_handler(CommandHandler("stop", stop_reminders))
        self.application.add_handler(CommandHandler("resume", resume_reminders))
        self.application.add_handler(CommandHandler("status", reminder_status))
        
        # Обработчик команды администратора
        self.application.add_handler(CommandHandler("admin", admin_panel))
        
        # Разговор для загрузки аудио администраторами
        audio_conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(
                self.audio_entry_point, 
                pattern=r"^add_audio_\d$"
            )],
            states={
                WAITING_AUDIO: [MessageHandler(
                    filters.AUDIO | filters.VOICE, 
                    receive_audio
                )],
                WAITING_TEXT: [MessageHandler(
                    filters.TEXT & ~filters.COMMAND, 
                    receive_text_description
                )]
            },
            fallbacks=[CommandHandler("cancel", cancel_admin_conversation)]
        )
        self.application.add_handler(audio_conv_handler)
        
        # Обработчики callback кнопок
        self.application.add_handler(CallbackQueryHandler(handle_pain_rating, pattern=r"^pain_\d$"))
        self.application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern=r"^(manage_|view_|back_to_|toggle_|change_|list_|broadcast)"))
        self.application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern=r"^(edit_audio_|delete_audio_|replace_audio_|edit_text_)\d$"))
        self.application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern=r"^set_time_\d+_\d+$"))
        
        # Обработчик неизвестных команд
        self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def audio_entry_point(self, update, context):
        """Точка входа для разговора загрузки аудио"""
        query = update.callback_query
        if not is_admin(query.from_user.id):
            await query.answer("У вас нет прав доступа.")
            return ConversationHandler.END
        
        pain_level = int(query.data.split("_")[-1])
        context.user_data['pain_level'] = pain_level
        await query.edit_message_text(
            f"Отправьте аудиосообщение для уровня боли {pain_level}:"
        )
        return WAITING_AUDIO
    
    async def unknown_command(self, update, context):
        """Обработчик неизвестных команд"""
        await update.message.reply_text(
            "Неизвестная команда. Используйте /help для просмотра доступных команд."
        )
    
    async def handle_text(self, update, context):
        """Обработчик обычных текстовых сообщений"""
        # Проверяем, не является ли это числом (оценка боли)
        text = update.message.text.strip()
        if text.isdigit() and 1 <= int(text) <= 5:
            # Создаем fake callback query для обработки оценки боли
            pain_level = int(text)
            await handle_pain_rating_from_text(update, context, pain_level)
        else:
            await update.message.reply_text(
                "Не понимаю ваше сообщение. Используйте /help для справки или /rate для оценки боли."
            )
    
    def setup_scheduler(self):
        """Настройка планировщика для ежедневных напоминаний"""
        # Получаем настройки времени из базы данных
        db = SessionLocal()
        try:
            hour_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_hour').first()
            minute_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_minute').first()
            enabled_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_enabled').first()
            
            hour = int(hour_setting.setting_value) if hour_setting else 10
            minute = int(minute_setting.setting_value) if minute_setting else 0
            enabled = enabled_setting.setting_value == 'true' if enabled_setting else True
            
            if enabled:
                # Добавляем ежедневную задачу
                self.application.job_queue.run_daily(
                    send_daily_reminder,
                    time=time(hour=hour, minute=minute),
                    name="daily_reminder"
                )
                logger.info(f"Планировщик настроен на {hour:02d}:{minute:02d}")
            else:
                logger.info("Ежедневные напоминания отключены")
                
        finally:
            db.close()
    
    def update_scheduler(self, hour: int, minute: int, enabled: bool):
        """Обновление настроек планировщика"""
        # Удаляем существующую задачу
        current_jobs = self.application.job_queue.get_jobs_by_name("daily_reminder")
        for job in current_jobs:
            job.schedule_removal()
        
        # Добавляем новую задачу если включена
        if enabled:
            self.application.job_queue.run_daily(
                send_daily_reminder,
                time=time(hour=hour, minute=minute),
                name="daily_reminder"
            )
            logger.info(f"Планировщик обновлен на {hour:02d}:{minute:02d}")
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск Spina Bot...")
        logger.info("Бот готов к работе!")
        
        # Запускаем бота
        self.application.run_polling(allowed_updates=['message', 'callback_query'])

async def handle_pain_rating_from_text(update, context, pain_level):
    """Обработка оценки боли из текстового сообщения"""
    from user_handlers import handle_pain_rating
    from telegram import CallbackQuery
    
    # Создаем объект, имитирующий CallbackQuery
    class FakeCallbackQuery:
        def __init__(self, message, user_id, data):
            self.message = message
            self.from_user = type('obj', (object,), {'id': user_id})
            self.data = data
        
        async def answer(self):
            pass
        
        async def edit_message_text(self, text, **kwargs):
            await self.message.reply_text(text, **kwargs)
    
    # Создаем fake callback query
    fake_query = FakeCallbackQuery(update.message, update.effective_user.id, f"pain_{pain_level}")
    
    # Обновляем update объект
    update.callback_query = fake_query
    
    # Вызываем обработчик
    await handle_pain_rating(update, context)

def main():
    """Главная функция"""
    try:
        # Проверяем BOT_TOKEN
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("❌ BOT_TOKEN не установлен в переменных окружения")
            return
        
        logger.info("✅ BOT_TOKEN найден")
        
        # Создаем директорию для базы данных если её нет
        data_dir = "/app/data" if os.path.exists("/app") else "data"
        if not os.path.exists(data_dir):
            logger.info(f"📁 Создание директории для базы данных: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)
        
        logger.info("✅ Директория для базы данных готова")
        
        # Инициализируем базу данных
        logger.info("🗄️ Инициализация базы данных...")
        try:
            create_tables()
            init_default_settings()
            logger.info("✅ База данных инициализирована")
        except Exception as db_error:
            logger.error(f"❌ Ошибка инициализации базы данных: {db_error}")
            return
        
        # Запускаем бота
        logger.info("🤖 Запуск бота...")
        bot = SpinaBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки. Завершение работы...")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        logger.info("Spina Bot остановлен.")

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
