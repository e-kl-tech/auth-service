# Auth Service - FastAPI + PostgreSQL

Микросервис для аутентификации и управления пользователями на FastAPI с PostgreSQL.

## 🚀 Функциональность

- Регистрация и аутентификация пользователей
- JWT токены для доступа
- Управление пользователями (CRUD)
- Docker контейнеризация

## 📦 Установка и запуск

### Требования
- Docker и Docker Compose
- Python 3.12 (для локальной разработки)

### Запуск с Docker

```bash
# Клонируйте репозиторий
git clone https://github.com/e-kl-tech/auth-service.git
cd auth-service

# Запустите контейнеры
docker-compose up -d --build

# Приложение будет доступно по http://localhost:8000
# Документация API: http://localhost:8000/docs
