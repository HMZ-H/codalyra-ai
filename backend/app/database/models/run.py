import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("tasks.id"), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(20), default="pending")
    started_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    exit_code: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", sa.JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), onupdate=sa.func.now())

    review_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("reviews.id"), nullable=True, index=True)

    task: Mapped["Task"] = relationship(back_populates="runs")
    review: Mapped["Review | None"] = relationship(back_populates="runs")
    checkpoints: Mapped[list["Checkpoint"]] = relationship(back_populates="run")
    trajectories: Mapped[list["Trajectory"]] = relationship(back_populates="run")
    evaluation: Mapped["Evaluation | None"] = relationship(back_populates="run", uselist=False)
