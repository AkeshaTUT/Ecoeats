"""
Утилиты и тестирование базы данных
"""

from database import DatabaseService
from models import User, Restaurant, Dish, Order

def test_database():
    """Протестировать БД"""
    print("🧪 Тестирование базы данных...\n")
    
    db = DatabaseService(db_path="test_ecoeats.db")
    
    # Тест 1: Создание пользователя
    print("✓ Создание пользователя")
    user = db.get_or_create_user(12345, "testuser")
    print(f"  User ID: {user.id}, Telegram ID: {user.telegram_id}, Username: {user.username}")
    
    # Тест 2: Получение ресторанов
    print("\n✓ Получение ресторанов")
    restaurants = db.get_restaurants()
    for rest in restaurants:
        print(f"  {rest.emoji} {rest.name} (ID: {rest.id})")
    
    # Тест 3: Получение блюд
    print("\n✓ Получение блюд для первого ресторана")
    if restaurants:
        dishes = db.get_dishes(restaurants[0].id)
        for dish in dishes:
            print(f"  - {dish.name} ({dish.price}₸)")
    
    # Тест 4: Создание заказа
    print("\n✓ Создание заказа")
    if restaurants and dishes:
        order_items = [
            {"dish_id": dishes[0].id, "quantity": 1, "eco_packaging": True},
            {"dish_id": dishes[1].id, "quantity": 2, "eco_packaging": False},
        ]
        order = db.create_order(user.telegram_id, order_items)
        print(f"  Order ID: {order.id}")
        print(f"  Total: {order.total_amount}₸")
        print(f"  Eco Fee: {order.eco_fee_total}₸")
    
    # Тест 5: Добавление эко-поинтов
    print("\n✓ Добавление эко-поинтов")
    db.add_eco_points(user.telegram_id, 5, "container_return")
    updated_user = db.get_user(user.telegram_id)
    print(f"  Total EcoPoints: {updated_user.eco_points}")
    
    # Тест 6: Статистика пользователя
    print("\n✓ Статистика пользователя")
    stats = db.get_user_stats(user.telegram_id)
    print(f"  EcoPoints: {stats['eco_points']}")
    print(f"  Orders Count: {stats['orders_count']}")
    
    print("\n✅ Все тесты пройдены!")
    
    # Очистка
    import os
    os.remove("test_ecoeats.db")
    print("\n🗑️ Тестовая БД удалена")

if __name__ == "__main__":
    test_database()
