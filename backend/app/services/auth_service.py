from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password
from app.database.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate
from app.services.github_service import GitHubService


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

    async def github_login(self, code: str) -> Token:
        token_data = await GitHubService.exchange_code_for_token(code)
        access_token = token_data["access_token"]

        gh_user = await GitHubService.get_github_user(access_token)
        github_id = gh_user["id"]
        github_username = gh_user["login"]
        avatar_url = gh_user.get("avatar_url")
        full_name = gh_user.get("name") or github_username

        email = gh_user.get("email")
        if not email:
            emails = await GitHubService.get_user_emails(access_token)
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary["email"] if primary else f"{github_username}@github.noreply.com"

        user = self.repo.get_by_github_id(github_id)
        if user:
            self.repo.update(user, {
                "github_token": access_token,
                "avatar_url": avatar_url,
                "github_username": github_username,
            })
        else:
            existing_email = self.repo.get_by_email(email)
            if existing_email:
                self.repo.update(existing_email, {
                    "github_id": github_id,
                    "github_username": github_username,
                    "github_token": access_token,
                    "avatar_url": avatar_url,
                })
                user = existing_email
            else:
                username = github_username
                if self.repo.get_by_username(username):
                    username = f"{github_username}-gh"
                user = self.repo.create({
                    "email": email,
                    "username": username,
                    "full_name": full_name,
                    "github_id": github_id,
                    "github_username": github_username,
                    "github_token": access_token,
                    "avatar_url": avatar_url,
                })

        jwt_token = create_access_token(subject=str(user.id))
        return Token(access_token=jwt_token)

    async def connect_github(self, user: User, code: str) -> User:
        token_data = await GitHubService.exchange_code_for_token(code)
        access_token = token_data["access_token"]

        gh_user = await GitHubService.get_github_user(access_token)
        github_id = gh_user["id"]

        existing = self.repo.get_by_github_id(github_id)
        if existing and existing.id != user.id:
            raise ConflictException("This GitHub account is already linked to another user")

        self.repo.update(user, {
            "github_id": github_id,
            "github_username": gh_user["login"],
            "github_token": access_token,
            "avatar_url": gh_user.get("avatar_url") or user.avatar_url,
        })
        return user
