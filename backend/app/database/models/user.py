import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    github_id: Mapped[int | None] = mapped_column(sa.BigInteger, unique=True, nullable=True, index=True)
    github_username: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    github_token: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    gemini_api_key_encrypted: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), onupdate=sa.func.now())

    projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    tasks: Mapped[list["Task"]] = relationship(back_populates="created_by")
