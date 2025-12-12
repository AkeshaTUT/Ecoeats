# Скрипт для развертывания на AWS (Windows PowerShell)

Write-Host "🚀 Начинаем развертывание EcoEats Bot на AWS..." -ForegroundColor Green

# Проверка наличия .env файла
if (-Not (Test-Path .env)) {
    Write-Host "⚠️  Файл .env не найден!" -ForegroundColor Yellow
    Write-Host "Создаю .env из примера..."
    Copy-Item .env.example .env
    Write-Host ""
    Write-Host "📝 ВАЖНО: Отредактируйте файл .env и добавьте ваш BOT_TOKEN!" -ForegroundColor Yellow
    Write-Host "   Используйте команду: notepad .env"
    Write-Host ""
    Read-Host "Нажмите Enter после того, как отредактируете .env"
}

# Чтение .env файла
Get-Content .env | ForEach-Object {
    if ($_ -match '^BOT_TOKEN=(.+)$') {
        $env:BOT_TOKEN = $matches[1]
    }
}

# Проверка, что токен установлен
if ([string]::IsNullOrEmpty($env:BOT_TOKEN) -or $env:BOT_TOKEN -eq "your_bot_token_here") {
    Write-Host "❌ Ошибка: BOT_TOKEN не настроен в .env файле!" -ForegroundColor Red
    Write-Host "Откройте .env и добавьте ваш токен от @BotFather"
    exit 1
}

Write-Host "✅ Конфигурация проверена" -ForegroundColor Green
Write-Host ""
Write-Host "🏗️  Сборка Docker образа..."

docker-compose build

Write-Host ""
Write-Host "🚀 Запуск бота..."
docker-compose up -d

Write-Host ""
Write-Host "✅ Бот запущен!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Полезные команды:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f     # Просмотр логов"
Write-Host "   docker-compose restart     # Перезапуск бота"
Write-Host "   docker-compose down        # Остановка бота"
Write-Host "   docker-compose ps          # Статус контейнера"
Write-Host ""
Write-Host "🌐 Проверьте бота в Telegram!" -ForegroundColor Green
