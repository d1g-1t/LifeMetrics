from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date, time
from decimal import Decimal
import structlog

from .states import RegistrationStates, FoodLoggingStates, WaterLoggingStates
from .keyboards import (
    get_main_menu_keyboard,
    get_gender_keyboard,
    get_activity_keyboard,
    get_goal_keyboard,
    get_meal_type_keyboard,
)
from apps.users.models import User, UserProfile
from apps.users.services import HealthCalculationService
from apps.food.services import FoodService, FoodLogService, WaterService

logger = structlog.get_logger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    
    try:
        user = User.objects.get(telegram_id=telegram_id)
        await message.answer(
            f"С возвращением, {user.username}! 👋\n\n"
            "Выберите действие:",
            reply_markup=get_main_menu_keyboard()
        )
    except User.DoesNotExist:
        user = User.objects.create(
            username=f"tg_{telegram_id}",
            telegram_id=telegram_id,
            telegram_username=message.from_user.username,
            telegram_first_name=message.from_user.first_name,
            telegram_last_name=message.from_user.last_name,
        )
        
        await message.answer(
            "Добро пожаловать в LifeMetrics! 🎯\n\n"
            "Давайте настроим ваш профиль.\n\n"
            "Укажите ваш пол:",
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_gender)
        await state.update_data(user_id=user.id)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(RegistrationStates.waiting_for_gender, F.data.in_(['gender_M', 'gender_F']))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data.split('_')[1]
    await state.update_data(gender=gender)
    
    await callback.message.edit_text(
        "Отлично! Теперь укажите ваш возраст (полных лет):"
    )
    await state.set_state(RegistrationStates.waiting_for_age)
    await callback.answer()


@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 10 or age > 120:
            await message.answer("Пожалуйста, укажите корректный возраст (10-120 лет):")
            return
        
        await state.update_data(age=age)
        await message.answer("Укажите ваш рост в см (например, 175):")
        await state.set_state(RegistrationStates.waiting_for_height)
    except ValueError:
        await message.answer("Пожалуйста, введите число:")


@router.message(RegistrationStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        if height < 100 or height > 250:
            await message.answer("Пожалуйста, укажите корректный рост (100-250 см):")
            return
        
        await state.update_data(height=height)
        await message.answer("Укажите ваш вес в кг (например, 70.5):")
        await state.set_state(RegistrationStates.waiting_for_weight)
    except ValueError:
        await message.answer("Пожалуйста, введите число:")


@router.message(RegistrationStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight < 30 or weight > 300:
            await message.answer("Пожалуйста, укажите корректный вес (30-300 кг):")
            return
        
        await state.update_data(weight=weight)
        await message.answer(
            "Выберите уровень вашей физической активности:",
            reply_markup=get_activity_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_activity_level)
    except ValueError:
        await message.answer("Пожалуйста, введите число:")


@router.callback_query(RegistrationStates.waiting_for_activity_level, F.data.startswith('activity_'))
async def process_activity(callback: CallbackQuery, state: FSMContext):
    activity_level = callback.data.split('_')[1]
    await state.update_data(activity_level=activity_level)
    
    await callback.message.edit_text(
        "Выберите вашу цель:",
        reply_markup=get_goal_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_goal)
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_for_goal, F.data.startswith('goal_'))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    goal = callback.data.split('_', 1)[1]
    await state.update_data(goal=goal)
    
    data = await state.get_data()
    user = User.objects.get(id=data['user_id'])
    
    from datetime import date, timedelta
    birth_year = date.today().year - data['age']
    date_of_birth = date(birth_year, 1, 1)
    
    profile = UserProfile.objects.create(
        user=user,
        gender=data['gender'],
        date_of_birth=date_of_birth,
        height=Decimal(str(data['height'])),
        weight=Decimal(str(data['weight'])),
        activity_level=data['activity_level'],
        goal=data['goal'],
    )
    
    result = HealthCalculationService.calculate_and_update_profile(profile)
    
    await callback.message.edit_text(
        f"✅ Профиль создан!\n\n"
        f"📊 Ваши показатели:\n"
        f"BMR: {result.bmr:.0f} ккал\n"
        f"TDEE: {result.tdee:.0f} ккал\n\n"
        f"🎯 Дневная норма:\n"
        f"Калории: {result.daily_calorie_target} ккал\n"
        f"Белки: {result.daily_protein_target}г\n"
        f"Углеводы: {result.daily_carbs_target}г\n"
        f"Жиры: {result.daily_fat_target}г\n\n"
        "Используйте меню для начала работы:",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "log_food")
async def start_food_logging(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите тип приема пищи:",
        reply_markup=get_meal_type_keyboard()
    )
    await state.set_state(FoodLoggingStates.waiting_for_meal_type)
    await callback.answer()


@router.callback_query(FoodLoggingStates.waiting_for_meal_type, F.data.startswith('meal_'))
async def process_meal_type(callback: CallbackQuery, state: FSMContext):
    meal_type = callback.data.split('_')[1]
    await state.update_data(meal_type=meal_type)
    
    await callback.message.edit_text(
        "Введите название продукта для поиска:"
    )
    await state.set_state(FoodLoggingStates.waiting_for_food_search)
    await callback.answer()


@router.message(FoodLoggingStates.waiting_for_food_search)
async def process_food_search(message: Message, state: FSMContext):
    query = message.text
    user = User.objects.get(telegram_id=message.from_user.id)
    
    foods = FoodService.search_foods(query, user, limit=10)
    
    if not foods:
        await message.answer(
            "Продукты не найдены. Попробуйте другой запрос или используйте /cancel для отмены."
        )
        return
    
    text = "Найденные продукты:\n\n"
    for i, food in enumerate(foods, 1):
        text += f"{i}. {food.name}"
        if food.brand:
            text += f" ({food.brand})"
        text += f" - {food.calories} ккал/100г\n"
    
    text += "\nВведите номер продукта:"
    
    await state.update_data(found_foods=[food.id for food in foods])
    await message.answer(text)
    await state.set_state(FoodLoggingStates.waiting_for_food_selection)


@router.message(FoodLoggingStates.waiting_for_food_selection)
async def process_food_selection(message: Message, state: FSMContext):
    try:
        selection = int(message.text) - 1
        data = await state.get_data()
        food_ids = data['found_foods']
        
        if selection < 0 or selection >= len(food_ids):
            await message.answer("Неверный номер. Попробуйте еще раз:")
            return
        
        food_id = food_ids[selection]
        await state.update_data(food_id=food_id)
        
        await message.answer("Укажите количество в граммах (например, 150):")
        await state.set_state(FoodLoggingStates.waiting_for_serving_amount)
    except ValueError:
        await message.answer("Пожалуйста, введите номер продукта:")


@router.message(FoodLoggingStates.waiting_for_serving_amount)
async def process_serving_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0 or amount > 5000:
            await message.answer("Пожалуйста, укажите корректное количество (1-5000г):")
            return
        
        data = await state.get_data()
        user = User.objects.get(telegram_id=message.from_user.id)
        
        food_log = FoodLogService.log_food(
            user=user,
            food_id=data['food_id'],
            serving_amount=Decimal(str(amount)),
            meal_type=data['meal_type'],
            log_date=date.today(),
        )
        
        await message.answer(
            f"✅ Записано!\n\n"
            f"Калории: {food_log.calories:.0f} ккал\n"
            f"Белки: {food_log.protein:.1f}г\n"
            f"Углеводы: {food_log.carbs:.1f}г\n"
            f"Жиры: {food_log.fat:.1f}г",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число:")


@router.callback_query(F.data == "log_water")
async def start_water_logging(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите количество выпитой воды в мл (например, 250):"
    )
    await state.set_state(WaterLoggingStates.waiting_for_amount)
    await callback.answer()


@router.message(WaterLoggingStates.waiting_for_amount)
async def process_water_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount <= 0 or amount > 5000:
            await message.answer("Пожалуйста, укажите корректное количество (1-5000 мл):")
            return
        
        user = User.objects.get(telegram_id=message.from_user.id)
        WaterService.log_water(user, amount, date.today())
        
        total = WaterService.get_daily_water_intake(user, date.today())
        
        await message.answer(
            f"✅ Записано {amount} мл!\n\n"
            f"Всего за сегодня: {total} мл",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число:")


@router.callback_query(F.data == "view_stats")
async def view_stats(callback: CallbackQuery):
    user = User.objects.get(telegram_id=callback.from_user.id)
    
    from apps.food.services import DailySummaryService
    summary = DailySummaryService.get_or_create_summary(user, date.today())
    
    text = (
        f"📊 Статистика за сегодня ({date.today().strftime('%d.%m.%Y')})\n\n"
        f"🍽 Питание:\n"
        f"Калории: {summary.total_calories:.0f} / {summary.target_calories or 0} ккал\n"
        f"Белки: {summary.total_protein:.1f}г\n"
        f"Углеводы: {summary.total_carbs:.1f}г\n"
        f"Жиры: {summary.total_fat:.1f}г\n\n"
        f"💧 Вода: {summary.water_intake_ml} мл\n\n"
    )
    
    if summary.target_calories:
        progress = (float(summary.total_calories) / summary.target_calories) * 100
        text += f"Прогресс: {progress:.1f}%"
    
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
    await callback.answer()



@router.message(Command("cancel"))
@router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.")
        return
    
    await state.clear()
    await message.answer(
        "Операция отменена.",
        reply_markup=get_main_menu_keyboard()
    )
