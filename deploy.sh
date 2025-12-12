#!/bin/bash

# Скрипт для быстрого развертывания на AWS EC2

echo "🚀 Начинаем развертывание EcoEats Bot на AWS..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "Установка Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker установлен! Пожалуйста, перезайдите в систему и запустите скрипт снова."
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    echo "Установка Docker Compose..."
    sudo apt install docker-compose -y
    echo "✅ Docker Compose установлен!"
fi

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создаю .env из примера..."
    cp .env.example .env
    echo ""
    echo "📝 ВАЖНО: Отредактируйте файл .env и добавьте ваш BOT_TOKEN!"
    echo "   Используйте команду: nano .env"
    echo ""
    read -p "Нажмите Enter после того, как отредактируете .env..."
fi

# Проверка, что токен установлен
source .env
if [ "$BOT_TOKEN" == "your_bot_token_here" ] || [ -z "$BOT_TOKEN" ]; then
    echo "❌ Ошибка: BOT_TOKEN не настроен в .env файле!"
    echo "Откройте .env и добавьте ваш токен от @BotFather"
    exit 1
fi

echo "✅ Конфигурация проверена"
echo ""
echo "🏗️  Сборка Docker образа..."
docker-compose build

echo ""
echo "🚀 Запуск бота..."
docker-compose up -d

echo ""
echo "✅ Бот запущен!"
echo ""
echo "📊 Полезные команды:"
echo "   docker-compose logs -f     # Просмотр логов"
echo "   docker-compose restart     # Перезапуск бота"
echo "   docker-compose down        # Остановка бота"
echo "   docker-compose ps          # Статус контейнера"
echo ""
echo "🌐 Проверьте бота в Telegram!"
