import logging

import httpx
from faststream import AckPolicy, FastStream
from faststream.exceptions import RejectMessage
from faststream.rabbit.annotations import RabbitMessage

from internal.broker import (
    broker,
    declare_topology,
    payments_exchange,
    payments_new_queue,
    payments_retry_queues,
)
from internal.modules.db.db import session_factory
from internal.modules.payment.gateway import FakePaymentGateway
from internal.modules.payment.schemas import PaymentEvent
from internal.modules.payment.use_case.process_payment import ProcessPaymentUseCase
from internal.modules.payment.webhook import WebhookNotifier
from internal.settings import settings

ATTEMPT_HEADER = "x-attempt"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastStream(broker)
gateway = FakePaymentGateway()
http_client = httpx.AsyncClient(timeout=settings.webhook_timeout)
notifier = WebhookNotifier(http_client)


@app.after_startup
async def setup() -> None:
    await declare_topology()


@app.after_shutdown
async def close_http_client() -> None:
    await http_client.aclose()


@broker.subscriber(payments_new_queue, payments_exchange, ack_policy=AckPolicy.REJECT_ON_ERROR)
async def handle_new_payment(event: PaymentEvent, message: RabbitMessage) -> None:
    attempt = int(message.headers.get(ATTEMPT_HEADER, 1))

    try:
        async with session_factory() as session:
            await ProcessPaymentUseCase(session, gateway, notifier).execute(event.payment_id)
    except Exception:
        if attempt >= settings.max_attempts:
            logger.exception("Payment %s failed after %d attempts, moving to DLQ", event.payment_id, attempt)
            raise RejectMessage()

        retry_queue = payments_retry_queues[attempt - 1]
        logger.warning(
            "Attempt %d for payment %s failed, retrying via %s",
            attempt, event.payment_id, retry_queue.name, exc_info=True,
        )
        await broker.publish(
            event.model_dump(mode="json"),
            exchange=payments_exchange,
            routing_key=retry_queue.name,
            headers={ATTEMPT_HEADER: attempt + 1},
            message_id=message.message_id,
            persist=True,
        )
