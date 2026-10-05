import datetime
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from internal.modules.db import BaseModel
from ..enums import Currency, PaymentStatus


class Payment(BaseModel):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2))
    currency: Mapped[Currency] = mapped_column(Enum(Currency, name="currency"))
    description: Mapped[str] = mapped_column(String)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status", values_callable=lambda e: [m.value for m in e]),
        default=PaymentStatus.PENDING,
    )
    idempotency_key: Mapped[str] = mapped_column(String, unique=True)
    webhook_url: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                          onupdate=func.now())
    processed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    webhook_sent_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
