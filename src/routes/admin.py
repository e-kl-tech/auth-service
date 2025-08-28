from fastapi import APIRouter, Depends, HTTPException, status

from src.database import db
from src.dependencies import get_current_user
from src.schemas import UserResponse, UserStatusResponse, UserActivateRequest

router = APIRouter(prefix="/admin", tags=["Администрирование"])


@router.get(
    "/users/{user_id}/status",
    response_model=UserStatusResponse,
    summary="Получить статус пользователя",
    description="Получение текущего статуса активности пользователя",
    operation_id="get_user_status"
)
async def get_user_status(
        user_id: int,
        current_user: dict = Depends(get_current_user)
):
    query = """
        SELECT id, email, is_active 
        FROM users 
        WHERE id = %s
    """
    user = db.execute_query(query, (user_id,))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    status_text = "активен" if user[0]['is_active'] else "деактивирован"

    return UserStatusResponse(
        id=user[0]['id'],
        email=user[0]['email'],
        is_active=user[0]['is_active'],
        message=f"Пользователь {status_text}"
    )


@router.patch(
    "/users/{user_id}/activate",
    response_model=UserStatusResponse,
    summary="Активировать пользователя",
    description="Активация пользователя по ID",
    operation_id="activate_user_admin"
)
async def activate_user(
        user_id: int,
        current_user: dict = Depends(get_current_user)
):
    query = """
        UPDATE users 
        SET is_active = TRUE 
        WHERE id = %s 
        RETURNING id, email, is_active
    """
    result = db.execute_query(query, (user_id,))

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return UserStatusResponse(
        id=result[0]['id'],
        email=result[0]['email'],
        is_active=result[0]['is_active'],
        message="Пользователь активирован"
    )


@router.patch(
    "/users/{user_id}/deactivate",
    response_model=UserStatusResponse,
    summary="Деактивировать пользователя",
    description="Деактивация пользователя по ID",
    operation_id="deactivate_user_admin"
)
async def deactivate_user_admin(
        user_id: int,
        current_user: dict = Depends(get_current_user)
):
    query = """
        UPDATE users 
        SET is_active = FALSE 
        WHERE id = %s 
        RETURNING id, email, is_active
    """
    result = db.execute_query(query, (user_id,))

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return UserStatusResponse(
        id=result[0]['id'],
        email=result[0]['email'],
        is_active=result[0]['is_active'],
        message="Пользователь деактивирован"
    )


@router.put(
    "/users/{user_id}/status",
    response_model=UserStatusResponse,
    summary="Установить статус пользователя",
    description="Установка статуса активности пользователя (True/False)",
    operation_id="set_user_status"
)
async def set_user_status(
        user_id: int,
        status_request: UserActivateRequest,
        current_user: dict = Depends(get_current_user)
):
    query = """
        UPDATE users 
        SET is_active = %s 
        WHERE id = %s 
        RETURNING id, email, is_active
    """
    result = db.execute_query(query, (status_request.is_active, user_id))

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    status_text = "активирован" if result[0]['is_active'] else "деактивирован"

    return UserStatusResponse(
        id=result[0]['id'],
        email=result[0]['email'],
        is_active=result[0]['is_active'],
        message=f"Пользователь {status_text}"
    )


@router.get(
    "/users/inactive",
    response_model=list[UserResponse],
    summary="Список неактивных пользователей",
    description="Получение списка деактивированных пользователей",
    operation_id="get_inactive_users"
)
async def get_inactive_users(current_user: dict = Depends(get_current_user)):
    query = """
        SELECT id, email, first_name, last_name, is_active, created_at
        FROM users 
        WHERE is_active = FALSE
        ORDER BY created_at DESC
    """

    try:
        users = db.execute_query(query)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка пользователей: {str(e)}",
        )