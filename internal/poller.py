import asyncio
import logging

from faststream.rabbit import RabbitBroker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.broker import broker, declare_topology, payments_exchange
from internal.modules.db.db import session_factory
from internal.modules.payment.enums import OutboxStatus
from internal.modules.payment.models import Outbox

logger = logging.getLogger(__name__)


class OutboxPoller:
    def __init__(
            self,
            broker: RabbitBroker,
            session_factory: async_sessionmaker[AsyncSession],
            batch_size: int = 100,
            interval: float = 1.0,
    ) -> None:
        self._broker = broker
        self._session_factory = session_factory
        self._batch_size = batch_size
        self._interval = interval

    async def run(self) -> None:
        while True:
            try:
                published = await self._publish_batch()
            except Exception:
                logger.exception("Failed to publish outbox batch")
                published = 0

            if published < self._batch_size:
                await asyncio.sleep(self._interval)

    async def _publish_batch(self) -> int:
        async with self._session_factory() as session:
            stmt = (
                select(Outbox)
                .where(Outbox.status == OutboxStatus.PENDING)
                .order_by(Outbox.created_at)
                .limit(self._batch_size)
                .with_for_update(skip_locked=True)
            )
            events = (await session.scalars(stmt)).all()

            for event in events:
                await self._broker.publish(
                    event.payload,
                    exchange=payments_exchange,
                    routing_key=event.queue,
                    message_id=str(event.id),
                    persist=True,
                )
                event.status = OutboxStatus.PUBLISHED

            await session.commit()

        if events:
            logger.info("Published %d outbox events", len(events))
        return len(events)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    async with broker:
        await declare_topology()
        await OutboxPoller(broker, session_factory).run()


if __name__ == "__main__":
    asyncio.run(main())
