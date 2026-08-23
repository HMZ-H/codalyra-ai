import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.jwt import decode_access_token
from app.database.models.user import User
from app.database.session import get_db
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException()
    except JWTError:
        raise UnauthorizedException()

    repo = UserRepository(db)
    user = repo.get_by_id(uuid.UUID(user_id))
    if user is None:
        raise UnauthorizedException()
    if not user.is_active:
        raise UnauthorizedException("Account is disabled")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
