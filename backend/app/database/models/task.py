import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("projects.id"), nullable=False, index=True)
    repository_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("repositories.id"), nullable=True, index=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
    language: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    difficulty: Mapped[str | None] = mapped_column(sa.String(20), nullable=True)
    status: Mapped[str] = mapped_column(sa.String(20), default="draft")
    expected_output: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    test_command: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    time_limit_seconds: Mapped[int] = mapped_column(sa.Integer, default=300)
    metadata_: Mapped[dict | None] = mapped_column("metadata", sa.JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), onupdate=sa.func.now())

    project: Mapped["Project"] = relationship(back_populates="tasks")
    repository: Mapped["Repository | None"] = relationship(back_populates="tasks")
    created_by: Mapped["User"] = relationship(back_populates="tasks")
    runs: Mapped[list["Run"]] = relationship(back_populates="task")
