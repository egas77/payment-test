from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue
from faststream.rabbit.schemas.queue import ClassicQueueArgs

from internal.settings import settings

broker = RabbitBroker(settings.rabbitmq_url)

payments_exchange = RabbitExchange("payments", type=ExchangeType.DIRECT, durable=True)
payments_dlx = RabbitExchange("payments.dlx", type=ExchangeType.DIRECT, durable=True)

payments_dlq = RabbitQueue("payments.new.dlq", durable=True)

_payments_new_args: ClassicQueueArgs = {
    "x-dead-letter-exchange": payments_dlx.name,
    "x-dead-letter-routing-key": payments_dlq.name,
}
payments_new_queue = RabbitQueue("payments.new", durable=True, arguments=_payments_new_args)


def _build_retry_queue(attempt: int) -> RabbitQueue:
    arguments: ClassicQueueArgs = {
        "x-message-ttl": settings.retry_base_delay_ms * 2 ** (attempt - 1),
        "x-dead-letter-exchange": payments_exchange.name,
        "x-dead-letter-routing-key": payments_new_queue.name,
    }
    return RabbitQueue(f"payments.new.retry.{attempt}", durable=True, arguments=arguments)


payments_retry_queues = [_build_retry_queue(attempt) for attempt in range(1, settings.max_attempts)]


async def declare_topology() -> None:
    exchange = await broker.declare_exchange(payments_exchange)
    dlx = await broker.declare_exchange(payments_dlx)

    for queue in (payments_new_queue, *payments_retry_queues):
        declared = await broker.declare_queue(queue)
        await declared.bind(exchange, routing_key=queue.name)

    dlq = await broker.declare_queue(payments_dlq)
    await dlq.bind(dlx, routing_key=payments_dlq.name)
