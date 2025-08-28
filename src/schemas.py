from datetime import datetime
from typing import Any, Optional
import re

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class TokenRequest(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }
    )


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия пользователя")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="Пароль пользователя")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str, info: Any) -> str:
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')

        checks = [
            (r'[A-Z]', 'заглавную букву'),
            (r'[a-z]', 'строчную букву'),
            (r'[0-9]', 'цифру'),
            (r'[!@#$%^&*(),.?":{}|<>]', 'специальный символ'),
        ]

        for pattern, requirement in checks:
            if not re.search(pattern, v):
                raise ValueError(f'Пароль должен содержать хотя бы одну {requirement}')

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!",
                "first_name": "Иван",
                "last_name": "Иванов"
            }
        }
    )


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Имя пользователя"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Фамилия пользователя"
    )
    is_active: Optional[bool] = Field(None, description="Статус активности аккаунта")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Петр",
                "last_name": "Петров",
                "is_active": True
            }
        }
    )


class UserResponse(UserBase):
    id: int = Field(..., description="ID пользователя")
    is_active: bool = Field(..., description="Статус активности аккаунта")
    created_at: datetime = Field(..., description="Дата и время создания аккаунта")

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Тип токена")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenData(BaseModel):
    user_id: Optional[int] = Field(None, description="ID пользователя")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }
    )


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Новый пароль"
    )

    @field_validator('new_password')
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')

        checks = [
            (r'[A-Z]', 'заглавную букву'),
            (r'[a-z]', 'строчную букву'),
            (r'[0-9]', 'цифру'),
            (r'[!@#$%^&*(),.?":{}|<>]', 'специальный символ'),
        ]

        for pattern, requirement in checks:
            if not re.search(pattern, v):
                raise ValueError(f'Пароль должен содержать хотя бы одну {requirement}')

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePassword456!"
            }
        }
    )


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя для сброса пароля")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com"
            }
        }
    )


class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="Токен для сброса пароля")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Новый пароль"
    )

    @field_validator('new_password')
    @classmethod
    def validate_reset_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')

        checks = [
            (r'[A-Z]', 'заглавную букву'),
            (r'[a-z]', 'строчную букву'),
            (r'[0-9]', 'цифру'),
            (r'[!@#$%^&*(),.?":{}|<>]', 'специальный символ'),
        ]

        for pattern, requirement in checks:
            if not re.search(pattern, v):
                raise ValueError(f'Пароль должен содержать хотя бы одну {requirement}')

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "reset_token_123456",
                "new_password": "NewSecurePassword456!"
            }
        }
    )


class UserListResponse(BaseModel):
    users: list[UserResponse] = Field(..., description="Список пользователей")
    total: int = Field(..., description="Общее количество пользователей")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "id": 1,
                        "email": "user1@example.com",
                        "first_name": "Иван",
                        "last_name": "Иванов",
                        "is_active": True,
                        "created_at": "2024-01-15T10:30:00"
                    },
                    {
                        "id": 2,
                        "email": "user2@example.com",
                        "first_name": "Петр",
                        "last_name": "Петров",
                        "is_active": True,
                        "created_at": "2024-01-16T11:45:00"
                    }
                ],
                "total": 2,
                "page": 1,
                "size": 10
            }
        }
    )


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Описание ошибки")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Пользователь с таким email уже существует"
            }
        }
    )


class SuccessResponse(BaseModel):
    message: str = Field(..., description="Сообщение об успехе")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Пользователь успешно создан"
            }
        }
    )


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Статус сервиса")
    version: str = Field(..., description="Версия API")
    timestamp: datetime = Field(..., description="Время проверки")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-20T12:00:00"
            }
        }
    )

class UserActivateRequest(BaseModel):
    is_active: bool = Field(..., description="Статус активности пользователя")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_active": True
            }
        }
    )

class UserStatusResponse(BaseModel):
    id: int = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    is_active: bool = Field(..., description="Статус активности")
    message: str = Field(..., description="Сообщение о результате операции")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "is_active": True,
                "message": "Пользователь активирован"
            }
        }
    )
