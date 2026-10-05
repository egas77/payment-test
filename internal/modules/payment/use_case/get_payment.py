import uuid

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from internal.modules.payment.exceptions import PaymentNotFound
from internal.modules.payment.models import Payment


class GetPaymentUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self, payment_id: uuid.UUID) -> Payment | None:
        stmt = sqlalchemy.select(Payment).where(Payment.id == payment_id)

        result = await self._session.scalar(stmt)
        if not result:
            raise PaymentNotFound(payment_id)

        return result
