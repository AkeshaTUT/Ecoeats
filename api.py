"""
REST API сервис для EcoEats бота
Используется для веб-интерфейса и интеграций
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import DatabaseService

app = FastAPI(title="EcoEats API", version="1.0.0")
db = DatabaseService(db_path="ecoeats.db")

# === PYDANTIC MODELS ===

class UserOut(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    eco_points: int
    orders_count: int
    created_at: datetime

class RestaurantOut(BaseModel):
    id: int
    name: str
    emoji: str
    description: Optional[str]

class DishOut(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]
    restaurant_id: int

class OrderItemOut(BaseModel):
    id: int
    dish_id: int
    quantity: int
    price: float
    eco_packaging: bool
    eco_fee: float

class OrderOut(BaseModel):
    id: int
    user_id: int
    total_amount: float
    eco_fee_total: float
    status: str
    created_at: datetime
    items: List[OrderItemOut]

class CreateOrderRequest(BaseModel):
    telegram_id: int
    items: List[dict]  # [{"dish_id": 1, "quantity": 1, "eco_packaging": True}]

class EcoPointsRequest(BaseModel):
    telegram_id: int
    amount: int
    reason: str

# === USER ENDPOINTS ===

@app.get("/api/users/{telegram_id}", response_model=UserOut)
async def get_user(telegram_id: int):
    """Получить информацию о пользователе"""
    user = db.get_user(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/users/{telegram_id}/{username}")
async def create_user(telegram_id: int, username: str):
    """Создать или получить пользователя"""
    user = db.get_or_create_user(telegram_id, username)
    return {"status": "ok", "user_id": user.id}

@app.get("/api/users/{telegram_id}/stats")
async def get_user_stats(telegram_id: int):
    """Получить статистику пользователя"""
    stats = db.get_user_stats(telegram_id)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return stats

# === RESTAURANT ENDPOINTS ===

@app.get("/api/restaurants", response_model=List[RestaurantOut])
async def get_restaurants():
    """Получить все рестораны"""
    restaurants = db.get_restaurants()
    return restaurants

@app.get("/api/restaurants/{restaurant_id}", response_model=RestaurantOut)
async def get_restaurant(restaurant_id: int):
    """Получить информацию о ресторане"""
    restaurant = db.get_restaurant(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

# === DISH ENDPOINTS ===

@app.get("/api/restaurants/{restaurant_id}/dishes", response_model=List[DishOut])
async def get_dishes(restaurant_id: int):
    """Получить меню ресторана"""
    dishes = db.get_dishes(restaurant_id)
    return dishes

@app.get("/api/dishes/{dish_id}", response_model=DishOut)
async def get_dish(dish_id: int):
    """Получить информацию о блюде"""
    dish = db.get_dish(dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish

# === ORDER ENDPOINTS ===

@app.post("/api/orders")
async def create_order(request: CreateOrderRequest):
    """Создать новый заказ"""
    try:
        order = db.create_order(request.telegram_id, request.items)
        return {
            "status": "ok",
            "order_id": order.id,
            "total_amount": order.total_amount,
            "eco_fee_total": order.eco_fee_total,
            "eco_points_earned": sum(1 for item in request.items if item.get("eco_packaging")) * 10
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# === ECO POINTS ENDPOINTS ===

@app.post("/api/eco-points/add")
async def add_eco_points(request: EcoPointsRequest):
    """Добавить экопоинты пользователю"""
    db.add_eco_points(request.telegram_id, request.amount, request.reason)
    user = db.get_user(request.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "status": "ok",
        "total_eco_points": user.eco_points
    }

# === HEALTH CHECK ===

@app.get("/api/health")
async def health_check():
    """Проверка статуса API"""
    return {
        "status": "healthy",
        "service": "EcoEats API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
