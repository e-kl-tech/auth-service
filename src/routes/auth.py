from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from src.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
)
from src.database import db
from src.schemas import LoginRequest, Token, TokenRequest, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создание нового аккаунта пользователя с email и паролем"
)
async def register(user: UserCreate):
    check_query = "SELECT id FROM users WHERE email = %s"
    existing_user = db.execute_query(check_query, (user.email,))

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    hashed_password = get_password_hash(user.password)

    insert_query = """
    INSERT INTO users (email, password_hash, first_name, last_name, is_active)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id, email, first_name, last_name, is_active, created_at
    """

    try:
        new_user = db.execute_query(
            insert_query,
            (user.email, hashed_password, user.first_name, user.last_name, True),
        )
        return new_user[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании пользователя: {str(e)}",
        )


@router.post(
    "/token",
    response_model=Token,
    summary="Получение JWT токена",
    description="Аутентификация пользователя по email и паролю для получения access token через JSON"
)
async def login_for_access_token(token_request: TokenRequest):
    """
    Получение JWT токена для аутентификации.

    - **email**: Email пользователя
    - **password**: Пароль пользователя
    """
    query = "SELECT id, email, password_hash, is_active FROM users WHERE email = %s"
    user = db.execute_query(query, (token_request.email,))

    if not user or not verify_password(token_request.password, user[0]['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user[0]['is_active']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь деактивирован",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user[0]['id'])},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/login",
    response_model=Token,
    summary="Альтернативный вход (совместимость)",
    description="Аутентификация через JSON body (аналогично /token)"
)
async def login(login_data: LoginRequest):
    """
    Альтернативный endpoint для входа (совместимость со старыми версиями).

    - **email**: Email пользователя
    - **password**: Пароль пользователя
    """
    query = "SELECT id, email, password_hash, is_active FROM users WHERE email = %s"
    user = db.execute_query(query, (login_data.email,))

    if not user or not verify_password(login_data.password, user[0]['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user[0]['is_active']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь деактивирован",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user[0]['id'])},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}