from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import SessionLocal, VideoLesson, BotSettings, User, UserResponse
from datetime import datetime
import logging

# Константы для администраторов
ADMIN_IDS = [354786612, 740144550]

# Состояния для разговоров
WAITING_VIDEO, WAITING_TITLE, WAITING_DESCRIPTION, WAITING_PAIN_LEVEL, WAITING_HOUR, WAITING_MINUTE = range(6)

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
        [InlineKeyboardButton("🎥 Управление видео-уроками", callback_data="manage_video")],
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
    
    if query.data == "manage_video":
        await show_video_management(query, context)
    elif query.data == "manage_time":
        await show_time_settings(query, context)
    elif query.data == "view_stats":
        await show_statistics(query, context)
    elif query.data == "manage_users":
        await show_user_management(query, context)
    elif query.data.startswith("add_video_"):
        pain_level = int(query.data.split("_")[-1])
        context.user_data['pain_level'] = pain_level
        await query.edit_message_text(
            f"Отправьте видео-урок для уровня боли {pain_level}:"
        )
        return WAITING_VIDEO
    elif query.data.startswith("edit_video_"):
        pain_level = int(query.data.split("_")[-1])
        await show_video_edit_options(query, context, pain_level)
    elif query.data == "back_to_main":
        await show_main_admin_panel(query, context)
    elif query.data == "toggle_reminders":
        await toggle_reminders(query, context)
    elif query.data == "change_time":
        await change_reminder_time(query, context)
    elif query.data.startswith("delete_video_"):
        pain_level = int(query.data.split("_")[-1])
        await delete_video_lesson(query, context, pain_level)
    elif query.data.startswith("replace_video_"):
        pain_level = int(query.data.split("_")[-1])
        context.user_data['pain_level'] = pain_level
        await query.edit_message_text(
            f"Отправьте новый видео-урок для уровня боли {pain_level}:"
        )
        return WAITING_VIDEO
    elif query.data.startswith("edit_title_"):
        pain_level = int(query.data.split("_")[-1])
        context.user_data['pain_level'] = pain_level
        context.user_data['edit_mode'] = 'title'
        await query.edit_message_text(
            f"Отправьте новое название для видео-урока уровня боли {pain_level}:"
        )
        return WAITING_TITLE
    elif query.data.startswith("edit_description_"):
        pain_level = int(query.data.split("_")[-1])
        context.user_data['pain_level'] = pain_level
        context.user_data['edit_mode'] = 'description'
        await query.edit_message_text(
            f"Отправьте новое описание для видео-урока уровня боли {pain_level}:"
        )
        return WAITING_DESCRIPTION
    elif query.data.startswith("set_time_"):
        time_parts = query.data.split("_")[2:]
        hour, minute = int(time_parts[0]), int(time_parts[1])
        await set_reminder_time(query, context, hour, minute)

async def show_video_management(query, context):
    """Показать меню управления видео-уроками"""
    db = SessionLocal()
    try:
        # Получаем существующие видео для каждого уровня боли
        video_lessons = db.query(VideoLesson).all()
        video_by_level = {}
        for video in video_lessons:
            video_by_level[video.pain_level] = video
        
        keyboard = []
        for level in range(1, 6):
            if level in video_by_level:
                text = f"✅ Уровень {level} (есть видео)"
                callback_data = f"edit_video_{level}"
            else:
                text = f"➕ Добавить для уровня {level}"
                callback_data = f"add_video_{level}"
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "🎥 *Управление видео-уроками*\n\n"
            "Выберите уровень боли для настройки:"
        )
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    finally:
        db.close()

async def show_video_edit_options(query, context, pain_level):
    """Показать опции редактирования для конкретного уровня боли"""
    keyboard = [
        [InlineKeyboardButton("🔄 Заменить видео", callback_data=f"replace_video_{pain_level}")],
        [InlineKeyboardButton("📝 Изменить название", callback_data=f"edit_title_{pain_level}")],
        [InlineKeyboardButton("📄 Изменить описание", callback_data=f"edit_description_{pain_level}")],
        [InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_video_{pain_level}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="manage_video")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Получаем информацию о текущем видео
    db = SessionLocal()
    try:
        video = db.query(VideoLesson).filter(VideoLesson.pain_level == pain_level).first()
        text = f"🎥 *Видео-урок для уровня боли {pain_level}*\n\n"
        if video:
            text += f"📝 Название: {video.title or 'Не задано'}\n"
            text += f"📄 Описание: {video.description or 'Не задано'}\n"
            if video.duration:
                minutes = video.duration // 60
                seconds = video.duration % 60
                text += f"⏱ Длительность: {minutes}:{seconds:02d}\n"
            text += f"📅 Создано: {video.created_at.strftime('%d.%m.%Y %H:%M')}"
        
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

async def receive_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение видео-урока от администратора"""
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    
    if 'pain_level' not in context.user_data:
        await update.message.reply_text("Ошибка: уровень боли не задан.")
        return ConversationHandler.END
    
    video = update.message.video or update.message.video_note
    if not video:
        await update.message.reply_text("Пожалуйста, отправьте видео-урок.")
        return WAITING_VIDEO
    
    context.user_data['video_file_id'] = video.file_id
    context.user_data['video_duration'] = video.duration if hasattr(video, 'duration') else None
    await update.message.reply_text(
        "Теперь отправьте название для этого видео-урока (или отправьте /skip чтобы пропустить):"
    )
    return WAITING_TITLE

async def receive_video_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение названия для видео-урока"""
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    
    title = None if update.message.text == '/skip' else update.message.text
    
    # Проверяем, это редактирование существующего видео или создание нового
    if context.user_data.get('edit_mode') == 'title':
        # Редактируем только название
        db = SessionLocal()
        try:
            pain_level = context.user_data['pain_level']
            video = db.query(VideoLesson).filter(VideoLesson.pain_level == pain_level).first()
            
            if video:
                video.title = title
                db.commit()
                await update.message.reply_text(
                    f"✅ Название видео-урока для уровня боли {pain_level} обновлено!"
                )
            else:
                await update.message.reply_text("❌ Видео-урок не найден.")
        finally:
            db.close()
        
        context.user_data.clear()
        return ConversationHandler.END
    else:
        # Создание нового видео - продолжаем к описанию
        context.user_data['video_title'] = title
        await update.message.reply_text(
            "Теперь отправьте описание для этого видео-урока (или отправьте /skip чтобы пропустить):"
        )
        return WAITING_DESCRIPTION

async def receive_video_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение описания для видео-урока"""
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    
    description = None if update.message.text == '/skip' else update.message.text
    
    # Проверяем, это редактирование существующего видео или создание нового
    if context.user_data.get('edit_mode') == 'description':
        # Редактируем только описание
        db = SessionLocal()
        try:
            pain_level = context.user_data['pain_level']
            video = db.query(VideoLesson).filter(VideoLesson.pain_level == pain_level).first()
            
            if video:
                video.description = description
                db.commit()
                await update.message.reply_text(
                    f"✅ Описание видео-урока для уровня боли {pain_level} обновлено!"
                )
            else:
                await update.message.reply_text("❌ Видео-урок не найден.")
        finally:
            db.close()
        
        context.user_data.clear()
        return ConversationHandler.END
    else:
        # Создание нового видео
        db = SessionLocal()
        try:
            pain_level = context.user_data['pain_level']
            video_file_id = context.user_data['video_file_id']
            video_title = context.user_data.get('video_title')
            video_duration = context.user_data.get('video_duration')
            
            # Удаляем старое видео для этого уровня боли если есть
            old_video = db.query(VideoLesson).filter(VideoLesson.pain_level == pain_level).first()
            if old_video:
                db.delete(old_video)
            
            # Создаем новое
            new_video = VideoLesson(
                pain_level=pain_level,
                file_id=video_file_id,
                title=video_title,
                description=description,
                duration=video_duration,
                created_by_admin=update.effective_user.id
            )
            db.add(new_video)
            db.commit()
            
            await update.message.reply_text(
                f"✅ Видео-урок для уровня боли {pain_level} успешно сохранен!"
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
        [InlineKeyboardButton("🎥 Управление видео-уроками", callback_data="manage_video")],
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

async def delete_video_lesson(query, context, pain_level):
    """Удаление видео-урока"""
    db = SessionLocal()
    try:
        video = db.query(VideoLesson).filter(VideoLesson.pain_level == pain_level).first()
        if video:
            db.delete(video)
            db.commit()
            await query.answer("Видео-урок удален")
        else:
            await query.answer("Видео-урок не найден")
        
        # Возвращаемся к управлению видео
        await show_video_management(query, context)
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