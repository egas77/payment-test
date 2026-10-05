from enum import Enum


class Currency(Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class OutboxStatus(Enum):
    PENDING = "pending"
    PUBLISHED = "published"
