import asyncio
import random

from internal.modules.payment.models import Payment


class FakePaymentGateway:
    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0, success_rate: float = 0.9) -> None:
        self._min_delay = min_delay
        self._max_delay = max_delay
        self._success_rate = success_rate

    async def charge(self, payment: Payment) -> bool:
        await asyncio.sleep(random.uniform(self._min_delay, self._max_delay))
        return random.random() < self._success_rate
