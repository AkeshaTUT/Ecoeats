import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import json
from typing import Dict, List

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Замените на ваш токен от @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Состояния FSM
class OrderStates(StatesGroup):
    choosing_restaurant = State()
    choosing_dish = State()
    choosing_packaging = State()
    viewing_cart = State()

# База данных (в памяти)
class Database:
    def __init__(self):
        self.users: Dict[int, dict] = {}
        self.restaurants = {
            "restaurant_a": {
                "name": "Restaurant A 🍕",
                "dishes": [
                    {"id": "a1", "name": "Пицца Маргарита", "price": 2500},
                    {"id": "a2", "name": "Паста Карбонара", "price": 3200},
                    {"id": "a3", "name": "Салат Цезарь", "price": 1800},
                ]
            },
            "restaurant_b": {
                "name": "Restaurant B 🍜",
                "dishes": [
                    {"id": "b1", "name": "Рамен", "price": 2800},
                    {"id": "b2", "name": "Суши сет", "price": 4500},
                    {"id": "b3", "name": "Том Ям", "price": 2200},
                ]
            },
            "restaurant_c": {
                "name": "Restaurant C 🍔",
                "dishes": [
                    {"id": "c1", "name": "Бургер Классик", "price": 2000},
                    {"id": "c2", "name": "Картофель фри", "price": 800},
                    {"id": "c3", "name": "Молочный коктейль", "price": 1200},
                ]
            }
        }
    
    def get_user(self, user_id: int) -> dict:
        if user_id not in self.users:
            self.users[user_id] = {
                "cart": [],
                "eco_points": 0,
                "orders_count": 0
            }
        return self.users[user_id]
    
    def add_to_cart(self, user_id: int, dish: dict, restaurant: str, eco_packaging: bool):
        user = self.get_user(user_id)
        user["cart"].append({
            "dish": dish,
            "restaurant": restaurant,
            "eco_packaging": eco_packaging,
            "eco_fee": 150 if eco_packaging else 0
        })
    
    def clear_cart(self, user_id: int):
        user = self.get_user(user_id)
        user["cart"] = []
    
    def add_eco_points(self, user_id: int, points: int):
        user = self.get_user(user_id)
        user["eco_points"] += points
    
    def calculate_total(self, user_id: int) -> tuple:
        user = self.get_user(user_id)
        total = 0
        eco_fee_total = 0
        for item in user["cart"]:
            total += item["dish"]["price"]
            eco_fee_total += item["eco_fee"]
        return total, eco_fee_total

db = Database()

# Клавиатуры
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
    keyboard = [
        [InlineKeyboardButton(text="Restaurant A 🍕", callback_data="rest_restaurant_a")],
        [InlineKeyboardButton(text="Restaurant B 🍜", callback_data="rest_restaurant_b")],
        [InlineKeyboardButton(text="Restaurant C 🍔", callback_data="rest_restaurant_c")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_dishes_keyboard(restaurant_id: str) -> InlineKeyboardMarkup:
    restaurant = db.restaurants[restaurant_id]
    keyboard = []
    for dish in restaurant["dishes"]:
        keyboard.append([InlineKeyboardButton(
            text=f"{dish['name']} – {dish['price']}₸",
            callback_data=f"dish_{restaurant_id}_{dish['id']}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад к ресторанам", callback_data="menu_restaurants")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_packaging_keyboard(restaurant_id: str, dish_id: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="♻️ Да, в экоупаковке (+150₸)", 
                            callback_data=f"pack_eco_{restaurant_id}_{dish_id}")],
        [InlineKeyboardButton(text="❌ Нет, обычная упаковка", 
                            callback_data=f"pack_regular_{restaurant_id}_{dish_id}")],
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

def get_return_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📦 Я хочу вернуть контейнеры", callback_data="confirm_return")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_button() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Обработчики команд
@router.message(Command("start"))
async def cmd_start(message: Message):
    user = db.get_user(message.from_user.id)
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

@router.message(Command("return"))
async def cmd_return(message: Message):
    await message.answer(
        "🔄 <b>Возврат контейнеров</b>\n\n"
        "Вы можете вернуть эко-контейнеры курьеру и получить бонусы.",
        reply_markup=get_return_keyboard(),
        parse_mode="HTML"
    )

# Обработчики кнопок
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌱 <b>Главное меню EcoEats</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_restaurants")
async def show_restaurants(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍽 <b>Выберите ресторан:</b>",
        reply_markup=get_restaurants_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("rest_"))
async def show_restaurant_menu(callback: CallbackQuery):
    restaurant_id = callback.data.replace("rest_", "")
    restaurant = db.restaurants[restaurant_id]
    
    await callback.message.edit_text(
        f"🍽 <b>{restaurant['name']}</b>\n\n"
        "Выберите блюдо:",
        reply_markup=get_dishes_keyboard(restaurant_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("dish_"))
async def choose_dish(callback: CallbackQuery):
    parts = callback.data.split("_")
    restaurant_id = parts[1]
    dish_id = parts[2]
    
    restaurant = db.restaurants[restaurant_id]
    dish = next(d for d in restaurant["dishes"] if d["id"] == dish_id)
    
    await callback.message.edit_text(
        f"🍽 <b>{dish['name']}</b>\n"
        f"💰 Цена: {dish['price']}₸\n\n"
        "Добавить в экоупаковке? (+150₸)",
        reply_markup=get_packaging_keyboard(restaurant_id, dish_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pack_"))
async def add_to_cart(callback: CallbackQuery):
    parts = callback.data.split("_")
    pack_type = parts[1]
    restaurant_id = parts[2]
    dish_id = parts[3]
    
    eco_packaging = pack_type == "eco"
    
    restaurant = db.restaurants[restaurant_id]
    dish = next(d for d in restaurant["dishes"] if d["id"] == dish_id)
    
    db.add_to_cart(callback.from_user.id, dish, restaurant["name"], eco_packaging)
    
    pack_text = "в экоупаковке ♻️" if eco_packaging else "в обычной упаковке"
    
    await callback.message.edit_text(
        f"✅ <b>Блюдо добавлено в корзину!</b>\n\n"
        f"🍽 {dish['name']}\n"
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
    user = db.get_user(user_id)
    
    if not user["cart"]:
        text = "🛒 <b>Ваша корзина пуста</b>\n\nДобавьте блюда из меню ресторанов!"
        keyboard = get_back_button()
    else:
        total, eco_fee_total = db.calculate_total(user_id)
        
        text = "🛒 <b>Ваш заказ:</b>\n\n"
        
        for i, item in enumerate(user["cart"], 1):
            pack_emoji = "♻️" if item["eco_packaging"] else "📦"
            pack_text = f"(экоупаковка +{item['eco_fee']}₸)" if item["eco_packaging"] else "(обычная)"
            text += f"– <b>Блюдо {i}</b> {pack_emoji} {pack_text} – {item['dish']['price'] + item['eco_fee']}₸\n"
        
        text += f"\n<b>Итого: {total + eco_fee_total}₸</b>"
        
        keyboard = get_cart_keyboard()
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    db.clear_cart(callback.from_user.id)
    await callback.message.edit_text(
        "🗑 <b>Корзина очищена</b>",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer("Корзина очищена")

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    user = db.get_user(callback.from_user.id)
    
    if not user["cart"]:
        await callback.answer("Корзина пуста!", show_alert=True)
        return
    
    # Подсчитываем бонусы за экоупаковку
    eco_count = sum(1 for item in user["cart"] if item["eco_packaging"])
    bonus_points = eco_count * 10
    
    db.add_eco_points(callback.from_user.id, bonus_points)
    user["orders_count"] += 1
    
    total, eco_fee_total = db.calculate_total(callback.from_user.id)
    
    db.clear_cart(callback.from_user.id)
    
    await callback.message.edit_text(
        "✅ <b>Спасибо! Ваш заказ оформлен 💚</b>\n\n"
        f"💰 Сумма заказа: {total + eco_fee_total}₸\n"
        f"🌿 Ваш бонус за использование экоупаковки: +{bonus_points} EcoPoints",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer("Заказ оформлен! 🎉")

@router.callback_query(F.data == "my_bonus")
async def my_bonus_callback(callback: CallbackQuery):
    await show_bonus(callback.from_user.id, callback.message, edit=True)
    await callback.answer()

async def show_bonus(user_id: int, message: Message, edit: bool = False):
    user = db.get_user(user_id)
    
    text = (
        f"🌿 <b>Ваши EcoPoints</b>\n\n"
        f"💚 У вас <b>{user['eco_points']}</b> EcoPoints\n\n"
        f"📊 Заказов сделано: {user['orders_count']}\n\n"
        "Бонусы можно использовать для скидок на следующие заказы!"
    )
    
    if edit:
        await message.edit_text(text, reply_markup=get_back_button(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=get_back_button(), parse_mode="HTML")

@router.callback_query(F.data == "return_containers")
async def return_containers(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔄 <b>Возврат контейнеров</b>\n\n"
        "Вы можете вернуть эко-контейнеры курьеру и получить бонусы.",
        reply_markup=get_return_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_return")
async def confirm_return(callback: CallbackQuery):
    db.add_eco_points(callback.from_user.id, 5)
    user = db.get_user(callback.from_user.id)
    
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

# Запуск бота
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
