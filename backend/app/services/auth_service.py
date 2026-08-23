from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password
from app.database.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, user_data: UserCreate) -> User:
        if self.repo.get_by_email(user_data.email):
            raise ConflictException("Email already registered")
        if self.repo.get_by_username(user_data.username):
            raise ConflictException("Username already taken")

        return self.repo.create({
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "hashed_password": hash_password(user_data.password),
        })

    def login(self, email: str, password: str) -> Token:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is disabled")

        access_token = create_access_token(subject=str(user.id))
        return Token(access_token=access_token)
