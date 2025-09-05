from fastapi import APIRouter, Depends

from src.db.models import User
from src.schemas.user_schemas import UserResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(auth_service.get_current_user),
):
    return current_user
