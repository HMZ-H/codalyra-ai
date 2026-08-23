import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Trajectory(Base):
    __tablename__ = "trajectories"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("runs.id"), nullable=False, index=True)
    sequence_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    action_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    action_input: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    action_output: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    duration_ms: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", sa.JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())

    run: Mapped["Run"] = relationship(back_populates="trajectories")
