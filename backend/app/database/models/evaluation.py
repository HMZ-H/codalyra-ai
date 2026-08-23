import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("runs.id"), unique=True, nullable=False)
    tests_passed: Mapped[int] = mapped_column(sa.Integer, default=0)
    tests_total: Mapped[int] = mapped_column(sa.Integer, default=0)
    score: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)
    feedback: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    evaluation_method: Mapped[str] = mapped_column(sa.String(50), default="auto")
    evaluated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    metadata_: Mapped[dict | None] = mapped_column("metadata", sa.JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())

    run: Mapped["Run"] = relationship(back_populates="evaluation")
