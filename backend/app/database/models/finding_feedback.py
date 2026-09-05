import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class FindingFeedback(Base):
    __tablename__ = "finding_feedback"
    __table_args__ = (
        sa.UniqueConstraint("review_id", "finding_hash", name="uq_finding_feedback"),
    )

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    review_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id"), nullable=False, index=True)
    finding_hash: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    action: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    agent: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    category: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    severity: Mapped[str | None] = mapped_column(sa.String(20), nullable=True)
    reason: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
