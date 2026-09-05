import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CustomRule(Base):
    __tablename__ = "custom_rules"
    __table_args__ = (
        sa.UniqueConstraint("project_id", "name", name="uq_custom_rule_project_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    pattern: Mapped[str] = mapped_column(sa.Text, nullable=False)
    severity: Mapped[str] = mapped_column(sa.String(20), nullable=False, default="warning")
    category: Mapped[str] = mapped_column(sa.String(100), nullable=False, default="custom-rule")
    message: Mapped[str] = mapped_column(sa.Text, nullable=False)
    suggestion: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    file_pattern: Mapped[str | None] = mapped_column(sa.String(200), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), onupdate=sa.func.now())
