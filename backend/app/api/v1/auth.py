import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.schemas.auth import GitHubCallbackRequest, LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

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


@router.get("/github")
def github_login_redirect():
    scope = "read:user user:email repo"
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope={scope}"
    )


@router.post("/github/callback", response_model=Token)
async def github_callback(
    data: GitHubCallbackRequest,
    db: Session = Depends(get_db),
) -> Token:
    service = AuthService(db)
    try:
        return await service.github_login(data.code)
    except ValueError as e:
        logger.error("GitHub login failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/github/connect", response_model=UserResponse)
async def connect_github(
    data: GitHubCallbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> User:
    service = AuthService(db)
    try:
        return await service.connect_github(current_user, data.code)
    except ValueError as e:
        logger.error("GitHub connect failed for user %s: %s", current_user.id, e)
        raise HTTPException(status_code=400, detail=str(e))
