from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User, UserResponse, AudioMessage
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Регистрируем пользователя в базе данных
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.telegram_id == user.id).first()
        if not existing_user:
            new_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            db.add(new_user)
            db.commit()
            logger.info(f"Новый пользователь зарегистрирован: {user.id}")
        else:
            # Обновляем информацию о пользователе
            existing_user.username = user.username
            existing_user.first_name = user.first_name
            existing_user.last_name = user.last_name
            existing_user.is_active = True
            db.commit()
    finally:
        db.close()
    
    welcome_text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот-помощник для заботы о здоровье вашей спины! 🌟\n\n"
        "Я буду ежедневно спрашивать о состоянии вашей спины и "
        "предлагать персональные упражнения и советы.\n\n"
        "🔢 Оцените боль от 1 до 5:\n"
        "1 - никакой боли\n"
        "2 - легкая боль\n"
        "3 - умеренная боль\n"
        "4 - сильная боль\n"
        "5 - очень сильная боль\n\n"
        "Давайте начнем! Как ваша спина сегодня?"
    )
    
    # Создаем клавиатуру с оценками боли
    keyboard = [
        [InlineKeyboardButton("1️⃣", callback_data="pain_1"),
         InlineKeyboardButton("2️⃣", callback_data="pain_2"),
         InlineKeyboardButton("3️⃣", callback_data="pain_3")],
        [InlineKeyboardButton("4️⃣", callback_data="pain_4"),
         InlineKeyboardButton("5️⃣", callback_data="pain_5")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "🆘 *Помощь*\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/rate - Оценить текущее состояние спины\n"
        "/stats - Моя статистика\n"
        "/stop - Отключить ежедневные напоминания\n"
        "/resume - Включить ежедневные напоминания\n"
        "/status - Проверить статус напоминаний\n"
        "/help - Эта справка\n\n"
        "💡 *Как пользоваться ботом:*\n"
        "• Каждый день я буду спрашивать о состоянии вашей спины\n"
        "• Оцените боль от 1 до 5\n"
        "• Получайте персональные аудио-упражнения\n"
        "• Следите за своим прогрессом\n\n"
        "Берегите свою спину! 💙"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def rate_pain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /rate для ручной оценки боли"""
    keyboard = [
        [InlineKeyboardButton("1️⃣", callback_data="pain_1"),
         InlineKeyboardButton("2️⃣", callback_data="pain_2"),
         InlineKeyboardButton("3️⃣", callback_data="pain_3")],
        [InlineKeyboardButton("4️⃣", callback_data="pain_4"),
         InlineKeyboardButton("5️⃣", callback_data="pain_5")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🩺 *Оценка состояния спины*\n\n"
        "Как ваша спина прямо сейчас?\n"
        "Оцените уровень боли от 1 до 5:"
    )
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_pain_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка оценки боли пользователем"""
    query = update.callback_query
    await query.answer()
    
    # Извлекаем уровень боли из callback_data
    pain_level = int(query.data.split('_')[1])
    user_id = query.from_user.id
    
    # Сохраняем ответ в базу данных
    db = SessionLocal()
    try:
        # Добавляем запись об ответе
        response = UserResponse(
            user_id=user_id,
            pain_rating=pain_level
        )
        db.add(response)
        
        # Обновляем информацию о пользователе
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            user.last_pain_rating = pain_level
            user.last_rating_date = datetime.utcnow()
        
        db.commit()
        
        # Получаем соответствующее аудиосообщение
        audio_message = db.query(AudioMessage).filter(AudioMessage.pain_level == pain_level).first()
        
        if audio_message:
            # Отправляем текстовое описание (если есть)
            if audio_message.text_description:
                await query.edit_message_text(
                    f"Спасибо за оценку! Уровень боли: {pain_level}\n\n"
                    f"{audio_message.text_description}"
                )
            else:
                await query.edit_message_text(
                    f"Спасибо за оценку! Уровень боли: {pain_level}\n\n"
                    "Вот персональная аудио-тренировка для вас:"
                )
            
            # Отправляем аудиосообщение
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=audio_message.file_id
            )
        else:
            # Если аудио не настроено для этого уровня
            await query.edit_message_text(
                f"Спасибо за оценку! Уровень боли: {pain_level}\n\n"
                "Заботьтесь о своей спине и не забывайте о регулярных упражнениях! 💙"
            )
            
            # Уведомляем о том, что нужно добавить аудио (только для логов)
            logger.warning(f"Нет аудиосообщения для уровня боли {pain_level}")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке оценки боли: {e}")
        await query.edit_message_text("Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()

async def user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику пользователя"""
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        # Получаем данные пользователя
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await update.message.reply_text("Вы не зарегистрированы. Нажмите /start")
            return
        
        # Получаем статистику ответов
        responses = db.query(UserResponse).filter(UserResponse.user_id == user_id).all()
        
        if not responses:
            await update.message.reply_text(
                "📊 *Ваша статистика*\n\n"
                "У вас пока нет записей о состоянии спины.\n"
                "Нажмите /rate для первой оценки!",
                parse_mode='Markdown'
            )
            return
        
        # Анализируем данные
        total_responses = len(responses)
        avg_pain = sum(r.pain_rating for r in responses) / total_responses
        last_response = max(responses, key=lambda x: x.response_date)
        
        # Статистика по уровням боли
        pain_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for response in responses:
            pain_counts[response.pain_rating] += 1
        
        # Последние 7 дней
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_responses = [r for r in responses if r.response_date >= seven_days_ago]
        
        text = (
            f"📊 *Ваша статистика*\n\n"
            f"📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}\n"
            f"💬 Всего оценок: {total_responses}\n"
            f"📈 Средний уровень боли: {avg_pain:.1f}\n"
            f"🕐 Последняя оценка: {last_response.response_date.strftime('%d.%m.%Y %H:%M')}\n"
            f"🎯 Последний уровень: {last_response.pain_rating}\n\n"
            f"📋 *Распределение по уровням:*\n"
        )
        
        for level, count in pain_counts.items():
            percentage = (count / total_responses) * 100 if total_responses > 0 else 0
            text += f"Уровень {level}: {count} раз ({percentage:.1f}%)\n"
        
        if recent_responses:
            avg_recent = sum(r.pain_rating for r in recent_responses) / len(recent_responses)
            text += f"\n📅 *За последние 7 дней:*\n"
            text += f"Оценок: {len(recent_responses)}\n"
            text += f"Средний уровень: {avg_recent:.1f}"
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
    finally:
        db.close()

async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Отправка ежедневного напоминания всем активным пользователям"""
    db = SessionLocal()
    try:
        active_users = db.query(User).filter(User.is_active == True).all()
        
        keyboard = [
            [InlineKeyboardButton("1️⃣", callback_data="pain_1"),
             InlineKeyboardButton("2️⃣", callback_data="pain_2"),
             InlineKeyboardButton("3️⃣", callback_data="pain_3")],
            [InlineKeyboardButton("4️⃣", callback_data="pain_4"),
             InlineKeyboardButton("5️⃣", callback_data="pain_5")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        reminder_text = (
            "🌅 *Доброе утро!*\n\n"
            "Время проверить состояние вашей спины.\n"
            "Как вы себя чувствуете сегодня?\n\n"
            "Оцените уровень боли от 1 до 5:"
        )
        
        sent_count = 0
        for user in active_users:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=reminder_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Ошибка отправки напоминания пользователю {user.telegram_id}: {e}")
                # Деактивируем пользователя если бот заблокирован
                if "blocked" in str(e).lower() or "user not found" in str(e).lower():
                    user.is_active = False
        
        db.commit()
        logger.info(f"Отправлено {sent_count} напоминаний из {len(active_users)} пользователей")
        
    finally:
        db.close()

async def stop_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отключение ежедневных напоминаний для пользователя"""
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        # Получаем или создаем пользователя
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await update.message.reply_text(
                "Вы не зарегистрированы. Нажмите /start для регистрации."
            )
            return
        
        # Отключаем напоминания для пользователя
        user.is_active = False
        db.commit()
        
        text = (
            "🔕 *Напоминания отключены*\n\n"
            "Вы больше не будете получать ежедневные напоминания.\n\n"
            "Вы всё ещё можете:\n"
            "• Оценивать боль вручную через /rate\n"
            "• Просматривать статистику через /stats\n"
            "• Включить напоминания обратно через /resume\n\n"
            "Берегите свою спину! 💙"
        )
        
        await update.message.reply_text(text, parse_mode='Markdown')
        logger.info(f"Пользователь {user_id} отключил напоминания")
        
    finally:
        db.close()

async def resume_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Включение ежедневных напоминаний для пользователя"""
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        # Получаем пользователя
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await update.message.reply_text(
                "Вы не зарегистрированы. Нажмите /start для регистрации."
            )
            return
        
        # Включаем напоминания для пользователя
        user.is_active = True
        db.commit()
        
        # Получаем настройки времени напоминаний
        from database import BotSettings
        hour_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_hour').first()
        minute_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_minute').first()
        enabled_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_enabled').first()
        
        current_hour = hour_setting.setting_value if hour_setting else "10"
        current_minute = minute_setting.setting_value if minute_setting else "0"
        reminders_enabled = enabled_setting.setting_value == 'true' if enabled_setting else True
        
        if reminders_enabled:
            text = (
                "🔔 *Напоминания включены*\n\n"
                f"Теперь вы снова будете получать ежедневные напоминания в {current_hour}:{current_minute:0>2}.\n\n"
                "Регулярная забота о спине - ключ к здоровью! 🌟\n\n"
                "Если хотите отключить напоминания, используйте /stop"
            )
        else:
            text = (
                "🔔 *Ваши напоминания включены*\n\n"
                "⚠️ Но сейчас глобальные напоминания отключены администратором.\n"
                "Вы получите уведомления, когда администратор их включит.\n\n"
                "Пока можете оценивать состояние спины вручную через /rate"
            )
        
        await update.message.reply_text(text, parse_mode='Markdown')
        logger.info(f"Пользователь {user_id} включил напоминания")
        
    finally:
        db.close()

async def reminder_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка статуса напоминаний для пользователя"""
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await update.message.reply_text(
                "Вы не зарегистрированы. Нажмите /start для регистрации."
            )
            return
        
        # Получаем глобальные настройки
        from database import BotSettings
        hour_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_hour').first()
        minute_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_minute').first()
        enabled_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_enabled').first()
        
        current_hour = hour_setting.setting_value if hour_setting else "10"
        current_minute = minute_setting.setting_value if minute_setting else "0"
        global_enabled = enabled_setting.setting_value == 'true' if enabled_setting else True
        
        user_status = "🟢 Включены" if user.is_active else "🔴 Отключены"
        global_status = "🟢 Включены" if global_enabled else "🔴 Отключены администратором"
        
        if user.is_active and global_enabled:
            final_status = f"✅ Вы будете получать напоминания в {current_hour}:{current_minute:0>2}"
        else:
            final_status = "❌ Напоминания не будут приходить"
        
        text = (
            f"📋 *Статус напоминаний*\n\n"
            f"Ваши напоминания: {user_status}\n"
            f"Глобальные напоминания: {global_status}\n"
            f"Время: {current_hour}:{current_minute:0>2}\n\n"
            f"{final_status}\n\n"
            f"Управление:\n"
            f"• /stop - отключить\n"
            f"• /resume - включить"
        )
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
    finally:
        db.close() 