from datetime import datetime

from pydantic import BaseModel


class UserInDB(BaseModel):
    id: int
    email: str
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreateInternal(BaseModel):
    email: str
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool = True