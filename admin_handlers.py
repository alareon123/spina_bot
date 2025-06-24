from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import SessionLocal, AudioMessage, BotSettings, User, UserResponse
from datetime import datetime
import logging

# Константы для администраторов
ADMIN_IDS = [354786612, 740144550]

# Состояния для разговоров
WAITING_AUDIO, WAITING_TEXT, WAITING_PAIN_LEVEL, WAITING_HOUR, WAITING_MINUTE = range(5)

logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная панель администратора"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет прав доступа к панели администратора.")
        return
    
    keyboard = [
        [InlineKeyboardButton("🎵 Управление аудио", callback_data="manage_audio")],
        [InlineKeyboardButton("⏰ Настройки времени", callback_data="manage_time")],
        [InlineKeyboardButton("📊 Статистика", callback_data="view_stats")],
        [InlineKeyboardButton("👥 Управление пользователями", callback_data="manage_users")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🔧 *Панель администратора*\n\n"
        "Выберите действие:"
    )
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка callback кнопок администратора"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("У вас нет прав доступа.")
        return
    
    if query.data == "manage_audio":
        await show_audio_management(query, context)
    elif query.data == "manage_time":
        await show_time_settings(query, context)
    elif query.data == "view_stats":
        await show_statistics(query, context)
    elif query.data == "manage_users":
        await show_user_management(query, context)
    elif query.data.startswith("add_audio_"):
        pain_level = int(query.data.split("_")[-1])
        context.user_data['pain_level'] = pain_level
        await query.edit_message_text(
            f"Отправьте аудиосообщение для уровня боли {pain_level}:"
        )
        return WAITING_AUDIO
    elif query.data.startswith("edit_audio_"):
        pain_level = int(query.data.split("_")[-1])
        await show_audio_edit_options(query, context, pain_level)
    elif query.data == "back_to_main":
        await show_main_admin_panel(query, context)
    elif query.data == "toggle_reminders":
        await toggle_reminders(query, context)
    elif query.data == "change_time":
        await change_reminder_time(query, context)
    elif query.data.startswith("delete_audio_"):
        pain_level = int(query.data.split("_")[-1])
        await delete_audio_message(query, context, pain_level)
    elif query.data.startswith("set_time_"):
        time_parts = query.data.split("_")[2:]
        hour, minute = int(time_parts[0]), int(time_parts[1])
        await set_reminder_time(query, context, hour, minute)

async def show_audio_management(query, context):
    """Показать меню управления аудиосообщениями"""
    db = SessionLocal()
    try:
        # Получаем существующие аудио для каждого уровня боли
        audio_messages = db.query(AudioMessage).all()
        audio_by_level = {}
        for audio in audio_messages:
            audio_by_level[audio.pain_level] = audio
        
        keyboard = []
        for level in range(1, 6):
            if level in audio_by_level:
                text = f"✅ Уровень {level} (есть аудио)"
                callback_data = f"edit_audio_{level}"
            else:
                text = f"➕ Добавить для уровня {level}"
                callback_data = f"add_audio_{level}"
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "🎵 *Управление аудиосообщениями*\n\n"
            "Выберите уровень боли для настройки:"
        )
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    finally:
        db.close()

async def show_audio_edit_options(query, context, pain_level):
    """Показать опции редактирования для конкретного уровня боли"""
    keyboard = [
        [InlineKeyboardButton("🔄 Заменить аудио", callback_data=f"replace_audio_{pain_level}")],
        [InlineKeyboardButton("📝 Изменить текст", callback_data=f"edit_text_{pain_level}")],
        [InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_audio_{pain_level}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="manage_audio")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Получаем информацию о текущем аудио
    db = SessionLocal()
    try:
        audio = db.query(AudioMessage).filter(AudioMessage.pain_level == pain_level).first()
        text = f"🎵 *Аудио для уровня боли {pain_level}*\n\n"
        if audio:
            text += f"📝 Текст: {audio.text_description or 'Не задан'}\n"
            text += f"📅 Создано: {audio.created_at.strftime('%d.%m.%Y %H:%M')}"
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    finally:
        db.close()

async def show_time_settings(query, context):
    """Показать настройки времени отправки напоминаний"""
    db = SessionLocal()
    try:
        hour_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_hour').first()
        minute_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_minute').first()
        enabled_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_enabled').first()
        
        current_hour = hour_setting.setting_value if hour_setting else "10"
        current_minute = minute_setting.setting_value if minute_setting else "0"
        is_enabled = enabled_setting.setting_value == 'true' if enabled_setting else True
        
        keyboard = [
            [InlineKeyboardButton("⏰ Изменить время", callback_data="change_time")],
            [InlineKeyboardButton(
                f"{'🔴 Отключить' if is_enabled else '🟢 Включить'} напоминания", 
                callback_data="toggle_reminders"
            )],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status = "🟢 Включены" if is_enabled else "🔴 Отключены"
        text = (
            f"⏰ *Настройки напоминаний*\n\n"
            f"Текущее время: {current_hour}:{current_minute:0>2}\n"
            f"Статус: {status}"
        )
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    finally:
        db.close()

async def show_statistics(query, context):
    """Показать статистику бота"""
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        total_responses = db.query(UserResponse).count()
        
        # Статистика по уровням боли за последние 30 дней
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_responses = db.query(UserResponse).filter(UserResponse.response_date >= thirty_days_ago).all()
        
        pain_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for response in recent_responses:
            pain_stats[response.pain_rating] += 1
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            f"📊 *Статистика бота*\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"✅ Активных: {active_users}\n"
            f"💬 Всего ответов: {total_responses}\n\n"
            f"📈 *Статистика боли (30 дней):*\n"
        )
        
        for level, count in pain_stats.items():
            text += f"Уровень {level}: {count} ответов\n"
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    finally:
        db.close()

async def show_user_management(query, context):
    """Показать управление пользователями"""
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        keyboard = [
            [InlineKeyboardButton("📝 Список пользователей", callback_data="list_users")],
            [InlineKeyboardButton("📢 Рассылка", callback_data="broadcast")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            f"👥 *Управление пользователями*\n\n"
            f"Всего пользователей: {total_users}\n"
            f"Активных: {active_users}"
        )
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    finally:
        db.close()

async def receive_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение аудиосообщения от администратора"""
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    
    if 'pain_level' not in context.user_data:
        await update.message.reply_text("Ошибка: уровень боли не задан.")
        return ConversationHandler.END
    
    audio = update.message.audio or update.message.voice
    if not audio:
        await update.message.reply_text("Пожалуйста, отправьте аудиосообщение.")
        return WAITING_AUDIO
    
    context.user_data['audio_file_id'] = audio.file_id
    await update.message.reply_text(
        "Теперь отправьте текстовое описание для этого аудио (или отправьте /skip чтобы пропустить):"
    )
    return WAITING_TEXT

async def receive_text_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение текстового описания для аудио"""
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    
    text_description = None if update.message.text == '/skip' else update.message.text
    
    # Сохраняем в базу данных
    db = SessionLocal()
    try:
        pain_level = context.user_data['pain_level']
        audio_file_id = context.user_data['audio_file_id']
        
        # Удаляем старое аудио для этого уровня боли если есть
        old_audio = db.query(AudioMessage).filter(AudioMessage.pain_level == pain_level).first()
        if old_audio:
            db.delete(old_audio)
        
        # Создаем новое
        new_audio = AudioMessage(
            pain_level=pain_level,
            file_id=audio_file_id,
            text_description=text_description,
            created_by_admin=update.effective_user.id
        )
        db.add(new_audio)
        db.commit()
        
        await update.message.reply_text(
            f"✅ Аудиосообщение для уровня боли {pain_level} успешно сохранено!"
        )
    finally:
        db.close()
    
    # Очищаем данные пользователя
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_admin_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена разговора администратора"""
    context.user_data.clear()
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

async def show_main_admin_panel(query, context):
    """Показать главную панель администратора"""
    keyboard = [
        [InlineKeyboardButton("🎵 Управление аудио", callback_data="manage_audio")],
        [InlineKeyboardButton("⏰ Настройки времени", callback_data="manage_time")],
        [InlineKeyboardButton("📊 Статистика", callback_data="view_stats")],
        [InlineKeyboardButton("👥 Управление пользователями", callback_data="manage_users")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🔧 *Панель администратора*\n\n"
        "Выберите действие:"
    )
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def toggle_reminders(query, context):
    """Переключение включения/отключения напоминаний"""
    db = SessionLocal()
    try:
        enabled_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_enabled').first()
        
        if enabled_setting:
            # Переключаем состояние
            new_value = 'false' if enabled_setting.setting_value == 'true' else 'true'
            enabled_setting.setting_value = new_value
            enabled_setting.updated_by_admin = query.from_user.id
            enabled_setting.updated_at = datetime.utcnow()
        else:
            # Создаем новую настройку
            new_setting = BotSettings(
                setting_name='reminder_enabled',
                setting_value='false',
                updated_by_admin=query.from_user.id
            )
            db.add(new_setting)
            new_value = 'false'
        
        db.commit()
        
        status_text = "включены" if new_value == 'true' else "отключены"
        await query.answer(f"Напоминания {status_text}")
        
        # Обновляем планировщик
        hour_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_hour').first()
        minute_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_minute').first()
        
        hour = int(hour_setting.setting_value) if hour_setting else 10
        minute = int(minute_setting.setting_value) if minute_setting else 0
        
        # Обновляем планировщик через контекст приложения
        if hasattr(context.application, 'spina_bot'):
            context.application.spina_bot.update_scheduler(hour, minute, new_value == 'true')
        
        # Показываем обновленные настройки времени
        await show_time_settings(query, context)
        
    finally:
        db.close()

async def change_reminder_time(query, context):
    """Изменение времени напоминаний"""
    keyboard = [
        [InlineKeyboardButton("09:00", callback_data="set_time_9_0")],
        [InlineKeyboardButton("10:00", callback_data="set_time_10_0")],
        [InlineKeyboardButton("11:00", callback_data="set_time_11_0")],
        [InlineKeyboardButton("12:00", callback_data="set_time_12_0")],
        [InlineKeyboardButton("🔙 Назад", callback_data="manage_time")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "⏰ *Выберите время напоминаний*\n\n"
        "Выберите один из предустановленных вариантов:"
    )
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def delete_audio_message(query, context, pain_level):
    """Удаление аудиосообщения"""
    db = SessionLocal()
    try:
        audio = db.query(AudioMessage).filter(AudioMessage.pain_level == pain_level).first()
        if audio:
            db.delete(audio)
            db.commit()
            await query.answer("Аудиосообщение удалено")
        else:
            await query.answer("Аудиосообщение не найдено")
        
        # Возвращаемся к управлению аудио
        await show_audio_management(query, context)
    finally:
        db.close()

async def set_reminder_time(query, context, hour, minute):
    """Установка времени напоминаний"""
    db = SessionLocal()
    try:
        # Обновляем или создаем настройки времени
        hour_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_hour').first()
        minute_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_minute').first()
        
        if hour_setting:
            hour_setting.setting_value = str(hour)
            hour_setting.updated_by_admin = query.from_user.id
            hour_setting.updated_at = datetime.utcnow()
        else:
            hour_setting = BotSettings(
                setting_name='reminder_hour',
                setting_value=str(hour),
                updated_by_admin=query.from_user.id
            )
            db.add(hour_setting)
        
        if minute_setting:
            minute_setting.setting_value = str(minute)
            minute_setting.updated_by_admin = query.from_user.id
            minute_setting.updated_at = datetime.utcnow()
        else:
            minute_setting = BotSettings(
                setting_name='reminder_minute',
                setting_value=str(minute),
                updated_by_admin=query.from_user.id
            )
            db.add(minute_setting)
        
        db.commit()
        
        # Проверяем включены ли напоминания
        enabled_setting = db.query(BotSettings).filter(BotSettings.setting_name == 'reminder_enabled').first()
        is_enabled = enabled_setting.setting_value == 'true' if enabled_setting else True
        
        # Обновляем планировщик через контекст приложения
        if hasattr(context.application, 'spina_bot'):
            context.application.spina_bot.update_scheduler(hour, minute, is_enabled)
        
        await query.answer(f"Время напоминаний установлено на {hour:02d}:{minute:02d}")
        
        # Показываем обновленные настройки времени
        await show_time_settings(query, context)
        
    finally:
        db.close() 