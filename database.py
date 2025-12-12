from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from models import Base, User, Restaurant, Dish, Order, OrderItem, EcoPoint
from datetime import datetime
from typing import List, Optional

class DatabaseService:
    def __init__(self, db_path: str = "ecoeats.db"):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._init_default_data()
    
    def get_session(self) -> Session:
        """Получить новую сессию"""
        return self.SessionLocal()
    
    def _init_default_data(self):
        """Инициализирует базу данных с тестовыми данными"""
        session = self.get_session()
        
        # Проверяем, есть ли уже данные
        if session.query(Restaurant).first():
            session.close()
            return
        
        # Добавляем рестораны
        restaurants = [
            Restaurant(name="Restaurant A", emoji="🍕", description="Итальянская кухня"),
            Restaurant(name="Restaurant B", emoji="🍜", description="Азиатская кухня"),
            Restaurant(name="Restaurant C", emoji="🍔", description="Американская кухня"),
        ]
        session.add_all(restaurants)
        session.commit()
        
        # Добавляем блюда
        dishes = [
            # Restaurant A
            Dish(restaurant_id=1, name="Пицца Маргарита", price=2500, description="Классическая пицца"),
            Dish(restaurant_id=1, name="Паста Карбонара", price=3200, description="Паста с беконом и сливками"),
            Dish(restaurant_id=1, name="Салат Цезарь", price=1800, description="Свежий салат"),
            # Restaurant B
            Dish(restaurant_id=2, name="Рамен", price=2800, description="Японская лапша"),
            Dish(restaurant_id=2, name="Суши сет", price=4500, description="Набор суши"),
            Dish(restaurant_id=2, name="Том Ям", price=2200, description="Острый тайский суп"),
            # Restaurant C
            Dish(restaurant_id=3, name="Бургер Классик", price=2000, description="Классический бургер"),
            Dish(restaurant_id=3, name="Картофель фри", price=800, description="Хрустящий картофель"),
            Dish(restaurant_id=3, name="Молочный коктейль", price=1200, description="Сладкий коктейль"),
        ]
        session.add_all(dishes)
        session.commit()
        session.close()
    
    # === USER METHODS ===
    def get_or_create_user(self, telegram_id: int, username: str = None) -> dict:
        """Получить или создать пользователя"""
        session = self.get_session()
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
        
        user_data = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "eco_points": user.eco_points,
            "orders_count": user.orders_count,
            "created_at": user.created_at
        }
        
        session.close()
        return user_data
    
    def get_user(self, telegram_id: int) -> dict:
        """Получить пользователя как словарь (избегаем проблем с DetachedInstanceError)"""
        session = self.get_session()
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        
        if user:
            user_data = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "eco_points": user.eco_points,
                "orders_count": user.orders_count,
                "created_at": user.created_at
            }
        else:
            user_data = None
        
        session.close()
        return user_data
    
    # === RESTAURANT METHODS ===
    def get_restaurants(self) -> List[Restaurant]:
        """Получить все рестораны"""
        session = self.get_session()
        restaurants = session.query(Restaurant).all()
        session.close()
        return restaurants
    
    def get_restaurant(self, restaurant_id: int) -> Optional[Restaurant]:
        """Получить ресторан по ID"""
        session = self.get_session()
        restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        session.close()
        return restaurant
    
    def get_restaurant_by_name(self, name: str) -> Optional[Restaurant]:
        """Получить ресторан по названию"""
        session = self.get_session()
        restaurant = session.query(Restaurant).filter(Restaurant.name == name).first()
        session.close()
        return restaurant
    
    # === DISH METHODS ===
    def get_dishes(self, restaurant_id: int) -> List[Dish]:
        """Получить блюда ресторана"""
        session = self.get_session()
        dishes = session.query(Dish).filter(Dish.restaurant_id == restaurant_id).all()
        session.close()
        return dishes
    
    def get_dish(self, dish_id: int) -> Optional[Dish]:
        """Получить блюдо по ID"""
        session = self.get_session()
        dish = session.query(Dish).filter(Dish.id == dish_id).first()
        session.close()
        return dish
    
    # === CART/ORDER METHODS ===
    def create_order(self, telegram_id: int, items: List[dict]) -> Order:
        """Создать заказ
        items: список {"dish_id": int, "quantity": int, "eco_packaging": bool}
        """
        session = self.get_session()
        
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            session.close()
            raise ValueError("User not found")
        
        total_amount = 0
        eco_fee_total = 0
        order_items = []
        eco_count = 0
        
        for item in items:
            dish = session.query(Dish).filter(Dish.id == item["dish_id"]).first()
            if not dish:
                continue
            
            quantity = item.get("quantity", 1)
            eco_packaging = item.get("eco_packaging", False)
            eco_fee = 150 if eco_packaging else 0
            
            item_price = dish.price * quantity
            total_amount += item_price
            eco_fee_total += eco_fee * quantity
            
            order_item = OrderItem(
                dish_id=dish.id,
                quantity=quantity,
                price=dish.price,
                eco_packaging=eco_packaging,
                eco_fee=eco_fee
            )
            order_items.append(order_item)
            
            if eco_packaging:
                eco_count += quantity
        
        order = Order(
            user_id=user.id,
            total_amount=total_amount,
            eco_fee_total=eco_fee_total,
            status="completed"
        )
        order.items = order_items
        
        session.add(order)
        session.flush()
        
        # Добавляем eco points
        bonus_points = eco_count * 10
        user.eco_points += bonus_points
        user.orders_count += 1
        
        eco_point = EcoPoint(
            user_id=user.id,
            amount=bonus_points,
            reason="eco_packaging"
        )
        session.add(eco_point)
        
        session.commit()
        session.close()
        
        return order
    
    def add_eco_points(self, telegram_id: int, amount: int, reason: str):
        """Добавить eco points"""
        session = self.get_session()
        
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            session.close()
            return
        
        user.eco_points += amount
        eco_point = EcoPoint(user_id=user.id, amount=amount, reason=reason)
        session.add(eco_point)
        session.commit()
        session.close()
    
    # === STATS METHODS ===
    def get_user_stats(self, telegram_id: int) -> dict:
        """Получить статистику пользователя"""
        session = self.get_session()
        
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            session.close()
            return {}
        
        total_spent = session.query(Order).filter(Order.user_id == user.id).count()
        eco_points = user.eco_points
        orders_count = user.orders_count
        
        stats = {
            "eco_points": eco_points,
            "orders_count": orders_count,
            "total_orders": total_spent
        }
        
        session.close()
        return stats
