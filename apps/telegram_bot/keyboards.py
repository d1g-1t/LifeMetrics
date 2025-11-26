from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🍽 Записать еду", callback_data="log_food"),
            InlineKeyboardButton(text="💧 Выпить воды", callback_data="log_water"),
        ],
        [
            InlineKeyboardButton(text="🏃 Тренировка", callback_data="log_workout"),
            InlineKeyboardButton(text="😴 Сон", callback_data="log_sleep"),
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="view_stats"),
            InlineKeyboardButton(text="🎯 Цели", callback_data="view_goals"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_gender_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="👨 Мужской", callback_data="gender_M"),
            InlineKeyboardButton(text="👩 Женский", callback_data="gender_F"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_activity_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Сидячий образ жизни", callback_data="activity_sedentary")],
        [InlineKeyboardButton(text="Легкая активность (1-3 раза/неделя)", callback_data="activity_light")],
        [InlineKeyboardButton(text="Умеренная активность (3-5 раз/неделя)", callback_data="activity_moderate")],
        [InlineKeyboardButton(text="Высокая активность (6-7 раз/неделя)", callback_data="activity_active")],
        [InlineKeyboardButton(text="Очень высокая активность", callback_data="activity_very_active")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_goal_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔻 Похудение", callback_data="goal_weight_loss")],
        [InlineKeyboardButton(text="⚖️ Поддержание веса", callback_data="goal_maintenance")],
        [InlineKeyboardButton(text="🔺 Набор мышечной массы", callback_data="goal_muscle_gain")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_meal_type_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🌅 Завтрак", callback_data="meal_breakfast"),
            InlineKeyboardButton(text="☀️ Обед", callback_data="meal_lunch"),
        ],
        [
            InlineKeyboardButton(text="🌙 Ужин", callback_data="meal_dinner"),
            InlineKeyboardButton(text="🍪 Перекус", callback_data="meal_snack"),
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
