import datetime
import logging
import uuid

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from internal.modules.payment.enums import PaymentStatus
from internal.modules.payment.gateway import FakePaymentGateway
from internal.modules.payment.models import Payment
from internal.modules.payment.webhook import WebhookNotifier

logger = logging.getLogger(__name__)


class ProcessPaymentUseCase:
    def __init__(self, session: AsyncSession, gateway: FakePaymentGateway, notifier: WebhookNotifier) -> None:
        self._session = session
        self._gateway = gateway
        self._notifier = notifier

    async def execute(self, payment_id: uuid.UUID) -> None:
        stmt = sqlalchemy.select(Payment).where(Payment.id == payment_id).with_for_update()
        payment: Payment | None = await self._session.scalar(stmt)

        if payment is None:
            logger.warning("Payment %s not found, skipping", payment_id)
            return

        if payment.status == PaymentStatus.PENDING:
            await self._charge(payment)
        else:
            logger.info("Payment %s already processed with status %s", payment_id, payment.status.value)

        if payment.webhook_sent_at is None:
            await self._send_webhook(payment)
        else:
            logger.info("Webhook for payment %s already sent, skipping", payment_id)

    async def _charge(self, payment: Payment) -> None:
        succeeded = await self._gateway.charge(payment)

        payment.status = PaymentStatus.SUCCEEDED if succeeded else PaymentStatus.FAILED
        payment.processed_at = datetime.datetime.now(datetime.UTC)
        await self._session.commit()

        logger.info("Payment %s processed with status %s", payment.id, payment.status.value)

    async def _send_webhook(self, payment: Payment) -> None:
        await self._notifier.notify(payment)

        payment.webhook_sent_at = datetime.datetime.now(datetime.UTC)
        await self._session.commit()

        logger.info("Webhook for payment %s delivered", payment.id)
