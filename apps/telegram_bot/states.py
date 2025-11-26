from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_activity_level = State()
    waiting_for_goal = State()
    waiting_for_target_weight = State()


class FoodLoggingStates(StatesGroup):
    waiting_for_meal_type = State()
    waiting_for_food_search = State()
    waiting_for_food_selection = State()
    waiting_for_serving_amount = State()


class WaterLoggingStates(StatesGroup):
    waiting_for_amount = State()


class WorkoutLoggingStates(StatesGroup):
    waiting_for_workout_type = State()
    waiting_for_duration = State()
    waiting_for_calories = State()


class SleepLoggingStates(StatesGroup):
    waiting_for_bedtime = State()
    waiting_for_wake_time = State()
    waiting_for_quality = State()
