import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.database.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_user(self, user_id: uuid.UUID) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    def update_user(self, user_id: uuid.UUID, update_data: UserUpdate) -> User:
        user = self.get_user(user_id)
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return user
        return self.repo.update(user, data)

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.repo.list_all(skip=skip, limit=limit)
