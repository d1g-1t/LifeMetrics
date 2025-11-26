# LifeMetrics

Production-ready бэкенд для трекинга здоровья с Telegram-ботом.

## Стек

| Категория | Технологии |
|-----------|------------|
| **API** | Django 5.0, Django Ninja 1.3, Pydantic 2.5 |
| **Runtime** | Uvicorn (ASGI), uvloop, httptools |
| **Database** | PostgreSQL 15, psycopg3 (async), connection pooling |
| **Cache** | Redis 7, hiredis, django-redis |
| **Queue** | Celery 5.3, Redis broker, Beat scheduler |
| **Bot** | aiogram 3.4, FSM, Redis storage |
| **Auth** | JWT (PyJWT), Argon2 password hashing |
| **Monitoring** | Sentry, structlog (JSON), health checks |
| **Deploy** | Docker, docker-compose, nginx, UV package manager |

## Функционал

- Дневник питания с расчётом КБЖУ
- BMR/TDEE калькулятор (Harris-Benedict)
- Трекинг тренировок и сна
- Система целей и достижений
- Telegram-бот с FSM-диалогами
- Автоматические напоминания (Celery Beat)

## Запуск

```bash
git clone https://github.com/d1g-1t/LifeMetrics.git
cd LifeMetrics
make setup
```

После установки:
1. Добавьте `TELEGRAM_BOT_TOKEN` в `.env`
2. `make start`
3. `make init-db`

**API:** http://localhost:8000/api/docs  
**Admin:** http://localhost:8000/admin

## Команды

```bash
make setup      # Установка
make start      # Запуск
make stop       # Остановка
make logs       # Логи
make migrate    # Миграции
make shell      # Django shell
make test       # Тесты
```

## Архитектура

```
apps/
├── core/          # Middleware, auth, базовые модели
├── users/         # Профили, JWT, BMR/TDEE расчёты
├── food/          # Питание, калории, макронутриенты
├── workouts/      # Тренировки
├── sleep/         # Сон
├── goals/         # Цели, достижения
└── telegram_bot/  # aiogram 3.x, FSM, handlers
```

## API

```
POST /api/auth/register     # Регистрация
POST /api/auth/login        # JWT токен
GET  /api/users/me          # Профиль
POST /api/food/log          # Запись еды
GET  /api/food/daily        # Дневная статистика
POST /api/workouts/log      # Тренировка
POST /api/sleep/log         # Сон
GET  /api/health            # Health check
```

## Лицензия

MIT
