import httpx

from internal.modules.payment.models import Payment


class WebhookDeliveryError(Exception):
    pass


class WebhookNotifier:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def notify(self, payment: Payment) -> None:
        payload = {
            "payment_id": str(payment.id),
            "status": payment.status.value,
            "amount": str(payment.amount),
            "currency": payment.currency.value,
            "metadata": payment.metadata_,
            "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
        }
        try:
            response = await self._client.post(payment.webhook_url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise WebhookDeliveryError(f"Webhook to {payment.webhook_url} failed: {exc}") from exc
