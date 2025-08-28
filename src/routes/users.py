from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.database import db
from src.dependencies import get_current_user
from src.schemas import UserListResponse, UserResponse

router = APIRouter(prefix="/users", tags=["Управление пользователями"])


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Получить пользователя по ID",
    description="Получение информации о пользователе по его идентификатору",
    operation_id="get_user_by_id"
)
async def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    query = """
        SELECT id, email, first_name, last_name, is_active, created_at 
        FROM users 
        WHERE id = %s
    """
    user = db.execute_query(query, (user_id,))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return user[0]


@router.get(
    "",
    response_model=UserListResponse,
    summary="Список пользователей",
    description="Получение списка всех пользователей с пагинацией",
    operation_id="get_all_users"
)
async def get_users(
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(10, ge=1, le=100, description="Размер страницы"),
        current_user: dict = Depends(get_current_user)
):
    offset = (page - 1) * size

    query = """
        SELECT id, email, first_name, last_name, is_active, created_at
        FROM users 
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """

    count_query = "SELECT COUNT(*) FROM users"

    try:
        users = db.execute_query(query, (size, offset))
        total_count = db.execute_query(count_query)[0]['count']

        return UserListResponse(
            users=users,
            total=total_count,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка пользователей: {str(e)}",
        )