from fastapi import HTTPException, status

from src.auth import verify_token
from src.database import db


async def get_current_user(token: str):
    user_id = verify_token(token)

    query = """
        SELECT id, email, first_name, last_name, is_active, created_at 
        FROM users 
        WHERE id = %s
    """
    user = db.execute_query(query, (user_id,))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user[0]