import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from database import DatabaseService

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Создайте файл .env и добавьте токен.")

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Инициализация БД
db = DatabaseService(db_path="ecoeats.db")

# Состояния FSM
class OrderStates(StatesGroup):
    choosing_restaurant = State()
    choosing_dish = State()
    choosing_packaging = State()
    viewing_cart = State()

# Глобальная корзина пользователя (хранится в памяти во время сеанса)
user_carts = {}

def get_user_cart(user_id: int):
    """Получить корзину пользователя"""
    if user_id not in user_carts:
        user_carts[user_id] = []
    return user_carts[user_id]

def clear_user_cart(user_id: int):
    """Очистить корзину пользователя"""
    if user_id in user_carts:
        user_carts[user_id] = []

# === КЛАВИАТУРЫ ===
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🍔 Меню ресторанов", callback_data="menu_restaurants")],
        [InlineKeyboardButton(text="🛒 Корзина", callback_data="view_cart")],
        [InlineKeyboardButton(text="🌿 Мои бонусы", callback_data="my_bonus")],
        [InlineKeyboardButton(text="🔄 Возврат контейнеров", callback_data="return_containers")],
        [InlineKeyboardButton(text="ℹ️ О сервисе", callback_data="about_service")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_restaurants_keyboard() -> InlineKeyboardMarkup:
    restaurants = db.get_restaurants()
    keyboard = []
    for rest in restaurants:
        keyboard.append([InlineKeyboardButton(
            text=f"{rest.emoji} {rest.name}",
            callback_data=f"rest|{rest.id}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_dishes_keyboard(restaurant_id: int) -> InlineKeyboardMarkup:
    dishes = db.get_dishes(restaurant_id)
    keyboard = []
    for dish in dishes:
        keyboard.append([InlineKeyboardButton(
            text=f"{dish.name} – {dish.price}₸",
            callback_data=f"dish|{restaurant_id}|{dish.id}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад к ресторанам", callback_data="menu_restaurants")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_packaging_keyboard(restaurant_id: int, dish_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="♻️ Да, в экоупаковке (+150₸)", 
                            callback_data=f"pack|eco|{restaurant_id}|{dish_id}")],
        [InlineKeyboardButton(text="❌ Нет, обычная упаковка", 
                            callback_data=f"pack|regular|{restaurant_id}|{dish_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_after_add_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить ещё", callback_data="menu_restaurants")],
        [InlineKeyboardButton(text="🛒 Перейти в корзину", callback_data="view_cart")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_cart_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="✔️ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton(text="❌ Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_button() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# === ОБРАБОТЧИКИ КОМАНД ===
@router.message(Command("start"))
async def cmd_start(message: Message):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "🌱 <b>Добро пожаловать в EcoEats!</b>\n\n"
        "Экологичная доставка еды 🌿\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "🌱 <b>Главное меню EcoEats</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("cart"))
async def cmd_cart(message: Message):
    await show_cart(message.from_user.id, message)

@router.message(Command("bonus"))
async def cmd_bonus(message: Message):
    await show_bonus(message.from_user.id, message)

# === ОБРАБОТЧИКИ КНОПОК ===
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "🌱 <b>Главное меню EcoEats</b>\n\n"
            "Выберите действие:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data == "menu_restaurants")
async def show_restaurants(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍽 <b>Выберите ресторан:</b>",
        reply_markup=get_restaurants_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("rest|"))
async def show_restaurant_menu(callback: CallbackQuery):
    restaurant_id = int(callback.data.split("|")[1])
    restaurant = db.get_restaurant(restaurant_id)
    
    if not restaurant:
        await callback.answer("Ресторан не найден", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"🍽 <b>{restaurant.emoji} {restaurant.name}</b>\n\n"
        "Выберите блюдо:",
        reply_markup=get_dishes_keyboard(restaurant_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("dish|"))
async def choose_dish(callback: CallbackQuery):
    parts = callback.data.split("|")
    restaurant_id = int(parts[1])
    dish_id = int(parts[2])
    
    dish = db.get_dish(dish_id)
    if not dish:
        await callback.answer("Блюдо не найдено", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"🍽 <b>{dish.name}</b>\n"
        f"💰 Цена: {dish.price}₸\n"
        f"📝 {dish.description or ''}\n\n"
        "Добавить в экоупаковке? (+150₸)",
        reply_markup=get_packaging_keyboard(restaurant_id, dish_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pack|"))
async def add_to_cart(callback: CallbackQuery):
    parts = callback.data.split("|")
    pack_type = parts[1]
    restaurant_id = int(parts[2])
    dish_id = int(parts[3])
    
    dish = db.get_dish(dish_id)
    if not dish:
        await callback.answer("Блюдо не найдено", show_alert=True)
        return
    
    eco_packaging = pack_type == "eco"
    
    # Добавляем в корзину
    cart = get_user_cart(callback.from_user.id)
    cart.append({
        "dish_id": dish_id,
        "dish_name": dish.name,
        "price": dish.price,
        "eco_packaging": eco_packaging,
        "eco_fee": 150 if eco_packaging else 0
    })
    
    pack_text = "в экоупаковке ♻️" if eco_packaging else "в обычной упаковке"
    
    await callback.message.edit_text(
        f"✅ <b>Блюдо добавлено в корзину!</b>\n\n"
        f"🍽 {dish.name}\n"
        f"💰 {dish.price}₸\n"
        f"📦 {pack_text}",
        reply_markup=get_after_add_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Добавлено в корзину! 🛒")

@router.callback_query(F.data == "view_cart")
async def view_cart_callback(callback: CallbackQuery):
    await show_cart(callback.from_user.id, callback.message, edit=True)
    await callback.answer()

async def show_cart(user_id: int, message: Message, edit: bool = False):
    cart = get_user_cart(user_id)
    
    if not cart:
        text = "🛒 <b>Ваша корзина пуста</b>\n\nДобавьте блюда из меню ресторанов!"
        keyboard = get_back_button()
    else:
        total = sum(item["price"] + item["eco_fee"] for item in cart)
        eco_fee_total = sum(item["eco_fee"] for item in cart)
        
        text = "🛒 <b>Ваш заказ:</b>\n\n"
        
        for i, item in enumerate(cart, 1):
            pack_emoji = "♻️" if item["eco_packaging"] else "📦"
            pack_text = f"(экоупаковка +{item['eco_fee']}₸)" if item["eco_packaging"] else "(обычная)"
            text += f"– <b>Блюдо {i}</b> {pack_emoji} {pack_text}\n"
            text += f"  {item['dish_name']} – {item['price'] + item['eco_fee']}₸\n"
        
        text += f"\n<b>Итого: {total}₸</b>"
        
        keyboard = get_cart_keyboard()
    
    if edit:
        try:
            await message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception:
            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    clear_user_cart(callback.from_user.id)
    await callback.message.edit_text(
        "🗑 <b>Корзина очищена</b>",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer("Корзина очищена")

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    cart = get_user_cart(callback.from_user.id)
    
    if not cart:
        await callback.answer("Корзина пуста!", show_alert=True)
        return
    
    try:
        # Подсчитываем бонусы за экоупаковку
        eco_count = sum(1 for item in cart if item["eco_packaging"])
        bonus_points = eco_count * 10
        
        # Создаем заказ в БД
        order_items = [
            {
                "dish_id": item["dish_id"],
                "quantity": 1,
                "eco_packaging": item["eco_packaging"]
            }
            for item in cart
        ]
        
        order = db.create_order(callback.from_user.id, order_items)
        total = sum(item["price"] + item["eco_fee"] for item in cart)
        
        clear_user_cart(callback.from_user.id)
        
        await callback.message.edit_text(
            "✅ <b>Спасибо! Ваш заказ оформлен 💚</b>\n\n"
            f"💰 Сумма заказа: {total}₸\n"
            f"🌿 Ваш бонус за использование экоупаковки: +{bonus_points} EcoPoints",
            reply_markup=get_back_button(),
            parse_mode="HTML"
        )
        await callback.answer("Заказ оформлен! 🎉")
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        await callback.answer("Ошибка при оформлении заказа", show_alert=True)

@router.callback_query(F.data == "my_bonus")
async def my_bonus_callback(callback: CallbackQuery):
    await show_bonus(callback.from_user.id, callback.message, edit=True)
    await callback.answer()

async def show_bonus(user_id: int, message: Message, edit: bool = False):
    user = db.get_user(user_id)
    
    if not user:
        # Создаем нового пользователя если его нет
        db.get_or_create_user(user_id)
        user = db.get_user(user_id)
    
    if user:
        text = (
            f"🌿 <b>Ваши EcoPoints</b>\n\n"
            f"💚 У вас <b>{user['eco_points']}</b> EcoPoints\n\n"
            f"📊 Заказов сделано: {user['orders_count']}\n\n"
            "Бонусы можно использовать для скидок на следующие заказы!"
        )
    else:
        text = "❌ Ошибка при получении данных пользователя"
    
    if edit:
        try:
            await message.edit_text(text, reply_markup=get_back_button(), parse_mode="HTML")
        except Exception:
            await message.answer(text, reply_markup=get_back_button(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=get_back_button(), parse_mode="HTML")

@router.callback_query(F.data == "return_containers")
async def return_containers(callback: CallbackQuery):
    keyboard = [
        [InlineKeyboardButton(text="📦 Я хочу вернуть контейнеры", callback_data="confirm_return")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
    ]
    
    try:
        await callback.message.edit_text(
            "🔄 <b>Возврат контейнеров</b>\n\n"
            "Вы можете вернуть эко-контейнеры курьеру и получить бонусы.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data == "confirm_return")
async def confirm_return(callback: CallbackQuery):
    db.add_eco_points(callback.from_user.id, 5, "container_return")
    user = db.get_user(callback.from_user.id)
    
    if not user:
        await callback.answer("Ошибка при получении данных", show_alert=True)
        return
    
    await callback.message.edit_text(
        "✅ <b>Отлично!</b>\n\n"
        "Курьер заберёт контейнеры при следующем заказе.\n"
        f"💚 +5 EcoPoints начислены\n\n"
        f"Ваш баланс: {user['eco_points']} EcoPoints",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer("Спасибо за заботу о природе! 🌱")

@router.callback_query(F.data == "about_service")
async def about_service(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ <b>О сервисе EcoEats</b>\n\n"
        "🌱 EcoEats — это экологичная доставка еды.\n\n"
        "♻️ Мы используем экоупаковку (+150–200₸) и начисляем бонусы за возврат контейнеров.\n\n"
        "💚 Наши преимущества:\n"
        "• Экологичная упаковка\n"
        "• Система бонусов EcoPoints\n"
        "• Возврат контейнеров для повторного использования\n"
        "• Забота о природе вместе с вами!\n\n"
        "🌍 Вместе мы делаем мир чище!",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()

# === ОБРАБОТЧИКИ ДЛЯ НЕПОДДЕРЖИВАЕМЫХ ОБНОВЛЕНИЙ ===
@router.message()
async def echo(message: Message):
    """Обработчик для сообщений, которые не совпадают с другими фильтрами"""
    pass

@router.callback_query()
async def handle_unknown_callback(callback: CallbackQuery):
    """Обработчик для неизвестных callback queries"""
    await callback.answer("Неизвестная команда", show_alert=False)

# === ЗАПУСК БОТА ===
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("🤖 Бот EcoEats запущен!")
    logger.info("🌱 Версия: MVP v1.0 с БД")
    logger.info("📊 База данных: ecoeats.db")
    logger.info("🚀 Режим: 24/7 (AWS Ready)")
    
    try:
        await dp.start_polling(bot, handle_signals=False)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"🛑 Бот остановлен с ошибкой: {e}")
        raise
