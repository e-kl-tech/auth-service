from fastapi import FastAPI

from src.routes import admin, auth, profile, users

app = FastAPI(
    title="Сервис Авторизации",
    version="1.0.0",
    description="Тестовое задание InstallBiz",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get(
    "/",
    summary="Главная страница API",
    description="Информация о сервисе авторизации и доступные endpoints"
)
async def root():
    return {
        "message": "Сервис авторизации API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth/*",
            "profile": "/users/me/*",
            "users": "/users/*"
        }
    }


app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(users.router)
app.include_router(admin.router)
