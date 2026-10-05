import datetime
import uuid
from typing import Any

from sqlalchemy import UUID, String, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from internal.modules.db import BaseModel
from internal.modules.payment.enums import OutboxStatus


class Outbox(BaseModel):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue: Mapped[str] = mapped_column(String)
    status: Mapped[OutboxStatus] = mapped_column(Enum(OutboxStatus, name="outbox_status", values_callable=lambda e: [m.value for m in e]), default=OutboxStatus.PENDING,
                                                 index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                          onupdate=func.now())
