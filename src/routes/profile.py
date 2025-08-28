from fastapi import APIRouter, Depends, HTTPException, status

from src.database import db
from src.dependencies import get_current_user
from src.schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/users/me", tags=["Профиль пользователя"])


@router.get(
    "",
    response_model=UserResponse,
    summary="Получить текущего пользователя",
    description="Получение информации о текущем аутентифицированном пользователе",
    operation_id="get_current_user_profile"
)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.put(
    "",
    response_model=UserResponse,
    summary="Обновить профиль",
    description="Обновление информации текущего пользователя",
    operation_id="update_user_profile"
)
async def update_user(
        user_update: UserUpdate,
        current_user: dict = Depends(get_current_user)
):
    update_fields = []
    update_values = []

    if user_update.first_name is not None:
        update_fields.append("first_name = %s")
        update_values.append(user_update.first_name)

    if user_update.last_name is not None:
        update_fields.append("last_name = %s")
        update_values.append(user_update.last_name)

    if user_update.is_active is not None:
        update_fields.append("is_active = %s")
        update_values.append(user_update.is_active)

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет полей для обновления"
        )

    update_values.append(current_user['id'])

    query = f"""
        UPDATE users 
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, email, first_name, last_name, is_active, created_at
    """

    try:
        updated_user = db.execute_query(query, update_values)
        return updated_user[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении пользователя: {str(e)}",
        )


@router.patch(
    "/deactivate",
    summary="Деактивировать аккаунт",
    description="Деактивация собственного аккаунта",
    operation_id="deactivate_own_account"
)
async def deactivate_user(current_user: dict = Depends(get_current_user)):
    query = "UPDATE users SET is_active = FALSE WHERE id = %s RETURNING id"
    result = db.execute_query(query, (current_user['id'],))

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return {"message": "Аккаунт успешно деактивирован"}