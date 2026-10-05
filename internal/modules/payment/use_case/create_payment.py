import uuid
from typing import Any

import sqlalchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from internal.modules.payment.models import Payment, Outbox
from internal.modules.payment.schemas import CreatePayment


class CreatePaymentUseCase:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def execute(self, data: CreatePayment, idempotency_key: str) -> Payment:
        exist_payment = await self._get_exist_payment(idempotency_key)
        if exist_payment is not None:
            return exist_payment

        new_payment_uuid = uuid.uuid4()

        new_payment = Payment(
            id=new_payment_uuid,
            amount=data.amount,
            currency=data.currency,
            description=data.description,
            idempotency_key=idempotency_key,
            webhook_url=str(data.webhook_url),
            metadata_=data.metadata
        )

        out_box_payload = self._build_outbox_metadata(new_payment)

        out_box = Outbox(
            queue="payments.new",
            payload=out_box_payload,
        )

        self._session.add(new_payment)
        self._session.add(out_box)

        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            exist_payment = await self._get_exist_payment(idempotency_key)
            if exist_payment is None:
                raise
            return exist_payment

        return new_payment

    async def _get_exist_payment(self, idempotency_key: str) -> Payment | None:
        stmt = sqlalchemy.select(Payment).where(Payment.idempotency_key == idempotency_key)

        return await self._session.scalar(stmt)

    def _build_outbox_metadata(self, payment: Payment) -> dict[str, Any]:
        return {
            'payment_id': str(payment.id),
        }
