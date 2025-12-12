from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(255), nullable=True)
    eco_points = Column(Integer, default=0)
    orders_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, eco_points={self.eco_points})>"


class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, index=True)
    emoji = Column(String(10))
    description = Column(String(500), nullable=True)
    
    dishes = relationship("Dish", back_populates="restaurant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Restaurant(name={self.name})>"


class Dish(Base):
    __tablename__ = "dishes"
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), index=True)
    name = Column(String(255))
    price = Column(Float)
    description = Column(String(500), nullable=True)
    
    restaurant = relationship("Restaurant", back_populates="dishes")
    order_items = relationship("OrderItem", back_populates="dish")
    
    def __repr__(self):
        return f"<Dish(name={self.name}, price={self.price})>"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    total_amount = Column(Float)
    eco_fee_total = Column(Float, default=0)
    status = Column(String(50), default="pending")  # pending, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total={self.total_amount})>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"), index=True)
    quantity = Column(Integer, default=1)
    price = Column(Float)
    eco_packaging = Column(Boolean, default=False)
    eco_fee = Column(Float, default=0)
    
    order = relationship("Order", back_populates="items")
    dish = relationship("Dish", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(dish_id={self.dish_id}, quantity={self.quantity})>"


class EcoPoint(Base):
    __tablename__ = "eco_points"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Integer)
    reason = Column(String(255))  # eco_packaging, container_return, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<EcoPoint(user_id={self.user_id}, amount={self.amount}, reason={self.reason})>"


# Инициализация базы данных
def init_db(db_path: str = "ecoeats.db"):
    """Инициализирует базу данных и создает таблицы"""
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return engine
