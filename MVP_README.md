# 🌱 EcoEats Bot - MVP v1.0

> Экологичный Telegram бот для доставки еды с системой бонусов EcoPoints и REST API

## 📦 Что включено

✅ **Telegram Bot** - асинхронный бот на aiogram  
✅ **SQLite Database** - хранение данных пользователей, заказов, бонусов  
✅ **REST API** - FastAPI сервис для интеграций и веб-интерфейса  
✅ **ORM Models** - SQLAlchemy модели данных  
✅ **Environment Config** - управление настройками через .env  

## 🚀 Быстрый старт

### 1️⃣ Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2️⃣ Конфигурация

Создайте файл `.env`:
```bash
BOT_TOKEN=8401864636:AAF3fDSK2Wd_wIdN313DrS5-s6ngnYTNRg0
```

(Замените на свой токен от [@BotFather](https://t.me/botfather))

### 3️⃣ Запуск

**Вариант A - Только бот:**
```bash
python bot_with_db.py
```

**Вариант B - Только API:**
```bash
python -m uvicorn api:app --reload
```
API будет доступен на `http://localhost:8000`
Swagger документация: `http://localhost:8000/docs`

**Вариант C - Оба сервиса (в разных терминалах):**
```bash
# Терминал 1 - Бот
python bot_with_db.py

# Терминал 2 - API
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## 📁 Структура файлов

```
ecoeats_bot/
│
├── 🤖 BOT FILES
│   ├── bot_with_db.py          ⭐ Основной бот (новая версия)
│   ├── bot_with_env.py         (старая версия - for reference)
│   └── bot.py                  (простая версия - for reference)
│
├── 🗄️ DATABASE
│   ├── models.py               🔸 ORM модели (User, Order, etc.)
│   ├── database.py             🔸 DatabaseService (CRUD)
│   └── ecoeats.db             (создается автоматически)
│
├── 🌐 API
│   ├── api.py                  🔸 REST API (FastAPI)
│   └── test_db.py              🔸 Тестирование БД
│
├── ⚙️ CONFIG
│   ├── .env                    🔸 Переменные окружения
│   ├── requirements.txt        🔸 Python зависимости
│   └── manage.py               🔸 Control panel
│
└── 📚 DOCS
    ├── README.md               (этот файл)
    ├── BACKEND_GUIDE.md        🔸 Технический гайд
    └── QUICKSTART.md           🔸 Быстрый старт
```

## 🎮 Команды бота

| Команда | Описание |
|---------|---------|
| `/start` | Главное меню |
| `/menu` | Показать рестораны |
| `/cart` | Просмотр корзины |
| `/bonus` | Просмотр EcoPoints |

## 🎯 Функциональность

### ✨ Для пользователя
- 🍽️ Просмотр меню ресторанов
- 🛒 Добавление блюд в корзину
- ♻️ Выбор эко-упаковки
- ✅ Оформление заказов
- 💚 Накопление бонусов EcoPoints
- 📦 Возврат контейнеров за бонусы
- 📊 Просмотр статистики

### 🔧 Для разработчика
- RESTful API с документацией
- SQLAlchemy ORM для работы с БД
- Асинхронная обработка событий
- Логирование и мониторинг
- Готовые тесты БД

## 💾 База данных

### Таблицы
- **users** - пользователи и их EcoPoints
- **restaurants** - рестораны
- **dishes** - меню блюд
- **orders** - заказы
- **order_items** - товары в заказе
- **eco_points** - история бонусов

### Пример запроса через API
```bash
# Получить информацию о пользователе
curl http://localhost:8000/api/users/123456

# Получить все рестораны
curl http://localhost:8000/api/restaurants

# Создать заказ
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456,
    "items": [
      {"dish_id": 1, "quantity": 1, "eco_packaging": true}
    ]
  }'
```

## 🧪 Тестирование

Протестировать БД:
```bash
python test_db.py
```

## 📊 Система бонусов

| Действие | Бонусы |
|---------|--------|
| Блюдо в эко-упаковке | +10 EcoPoints |
| Возврат контейнера | +5 EcoPoints |

## 🔐 Безопасность

- Токен хранится в `.env` файле (не в коде)
- SQLAlchemy защищает от SQL injection
- Асинхронная обработка предотвращает блокировки

## 📈 Масштабирование

**Текущая архитектура:**
- SQLite (локальное хранилище)
- Memory storage для FSM

**Для продакшена рекомендуется:**
- PostgreSQL вместо SQLite
- Redis для кэша и FSM
- Docker контейнеризация
- CI/CD пайплайн
- Prometheus для мониторинга

## 🐛 Отладка

**Очистить БД:**
```bash
rm ecoeats.db
```

**Просмотр логов:**
```bash
# Логи выводятся в консоль при запуске
python bot_with_db.py
```

**Проверить статус API:**
```bash
curl http://localhost:8000/api/health
```

## 📚 Документация

- **BACKEND_GUIDE.md** - Технические детали
- **QUICKSTART.md** - Быстрый старт
- **TESTING_SCENARIOS.md** - Сценарии тестирования
- **API Swagger** - http://localhost:8000/docs (при запущенном API)

## 🤝 Контрибьютинг

Рекомендации для разработки:
1. Создайте ветку для новой функции
2. Напишите тесты
3. Обновите документацию
4. Отправьте pull request

## 📝 Лицензия

MIT License

## 👨‍💻 Стек технологий

```
┌─────────────────────┐
│   Telegram User     │
└──────────┬──────────┘
           │
     ┌─────▼─────┐
     │ aiogram   │ (Bot)
     └─────┬─────┘
           │
     ┌─────▼─────────┐
     │  FastAPI      │ (API)
     └─────┬─────────┘
           │
     ┌─────▼──────────┐
     │  SQLAlchemy    │
     └─────┬──────────┘
           │
     ┌─────▼──────────┐
     │    SQLite      │ (Database)
     └────────────────┘
```

## 🎯 Дальнейшие этапы

- [ ] Добавить платежи (Stripe, Robokassa)
- [ ] Реализовать отслеживание доставки
- [ ] Добавить админ-панель
- [ ] Интеграция с сервисом доставки
- [ ] ML рекомендации блюд
- [ ] Веб-версия
- [ ] мобильное приложение

## ❓ FAQ

**Q: Как изменить меню?**  
A: Отредактируйте `_init_default_data()` в `database.py` или используйте API

**Q: Как добавить нового ресторана?**  
A: Используйте API endpoint или добавьте в БД напрямую через SQLite CLI

**Q: Бот не отвечает**  
A: Проверьте:
- Запущен ли процесс: `python bot_with_db.py`
- Правильный ли токен в `.env`
- Есть ли интернет соединение

**Q: Как развернуть на сервер?**  
A: Используйте Docker или systemd сервис. Замените SQLite на PostgreSQL.

---

**Made with ❤️ for the environment** 🌱
