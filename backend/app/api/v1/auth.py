from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.database.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> User:
    service = AuthService(db)
    return service.register(user_data)


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> Token:
    service = AuthService(db)
    return service.login(login_data.email, login_data.password)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user
