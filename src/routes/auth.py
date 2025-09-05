from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Security
from fastapi.security import (HTTPAuthorizationCredentials, HTTPBearer,
                              OAuth2PasswordRequestForm)
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import Database
from src.repository import users as repository_users
from src.schemas.user_schemas import TokenModel, UserCreate, UserResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
database = Database()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(body: UserCreate, db: AsyncSession = Depends(database.get_db)):
    exist_user = await repository_users.get_user_by_email(str(body.email), db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return {"id": new_user.id, "email": new_user.email}


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(database.get_db),
):
    user = await repository_users.get_user_by_email(body.username, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    new_access_token = await auth_service.create_access_token(data={"sub": user.email})
    new_refresh_token = await auth_service.create_refresh_token(
        data={"sub": user.email}
    )
    await repository_users.update_refresh_token(user, new_refresh_token, db)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(database.get_db),
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_refresh_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    new_access_token = await auth_service.create_access_token(data={"sub": email})
    new_refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_refresh_token(user, new_refresh_token, db)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
