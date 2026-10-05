import datetime
import uuid
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, ConfigDict

from internal.modules.payment.enums import Currency, PaymentStatus


class CreatePayment(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: Currency
    description: str = Field(max_length=512)
    metadata: dict[str, Any] = Field(default_factory=dict)
    webhook_url: HttpUrl


class PaymentCreateSuccess(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: uuid.UUID = Field(validation_alias="id")
    status: PaymentStatus
    created_at: datetime.datetime


class PaymentInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any] = Field(validation_alias="metadata_")
    webhook_url: str
    status: PaymentStatus
    created_at: datetime.datetime
    processed_at: datetime.datetime | None
    idempotency_key: str


class PaymentEvent(BaseModel):
    payment_id: uuid.UUID
