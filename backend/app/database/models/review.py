import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("projects.id"), nullable=False, index=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id"), nullable=False, index=True)
    pr_title: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    diff_content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    status: Mapped[str] = mapped_column(sa.String(20), default="pending")
    overall_score: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    summary: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    findings_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    baseline_summary: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    baseline_score: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", sa.JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), onupdate=sa.func.now())

    project: Mapped["Project"] = relationship(back_populates="reviews")
    created_by: Mapped["User"] = relationship()
    runs: Mapped[list["Run"]] = relationship(back_populates="review")
