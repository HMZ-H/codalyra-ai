import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    url: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    clone_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    default_branch: Mapped[str] = mapped_column(sa.String(100), default="main")
    language: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), onupdate=sa.func.now())

    project: Mapped["Project"] = relationship(back_populates="repositories")
    tasks: Mapped[list["Task"]] = relationship(back_populates="repository")
