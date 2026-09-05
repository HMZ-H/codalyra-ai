import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AgentConfig(Base):
    __tablename__ = "agent_configs"
    __table_args__ = (
        sa.UniqueConstraint("project_id", "agent_type", name="uq_agent_config_project_agent"),
    )

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    custom_prompt: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    temperature: Mapped[float] = mapped_column(sa.Float, default=0.2)
    is_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), onupdate=sa.func.now())
