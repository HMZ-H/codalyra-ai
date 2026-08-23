import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("runs.id"), nullable=False, index=True)
    sequence_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    content_hash: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    diff_content: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())

    run: Mapped["Run"] = relationship(back_populates="checkpoints")
