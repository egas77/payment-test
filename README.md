# Payments Service

Сервис асинхронной обработки платежей: принимает платеж, обрабатывает через эмуляцию шлюза и отправляет результат на webhook.

Стек: FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, RabbitMQ (FastStream), Alembic, Docker.

## Запуск

```bash
cp .env.example .env
docker compose up -d --build
```

- API: http://localhost:8000/docs
- RabbitMQ: http://localhost:15673 (`rabbit_user` / `rabbit_pass`)

Если порт 8000 занят: `API_PORT=8001 docker compose up -d --build`.

## Сервисы

- `api` — создание и получение платежей
- `outbox-poller` — отправляет события из таблицы `outbox` в RabbitMQ
- `consumer` — обрабатывает платеж, обновляет статус, шлет webhook
- `migrations` — применяет миграции при старте
- `postgres`, `rabbitmq`

## API

Во всех запросах нужен заголовок `X-API-Key` (значение из `.env`).

Создать платеж:

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "X-API-Key: change-me" \
  -H "Idempotency-Key: order-1001" \
  -H "Content-Type: application/json" \
  -d '{"amount": "1500.00", "currency": "RUB", "description": "Order #1001", "metadata": {"order_id": 1001}, "webhook_url": "https://example.com/webhook"}'
```

```json
{"payment_id": "cc992b11-680d-431c-aa29-f7c879e3b122", "status": "pending", "created_at": "2026-10-05T13:56:48.494775Z"}
```

Получить платеж:

```bash
curl http://localhost:8000/api/v1/payments/cc992b11-680d-431c-aa29-f7c879e3b122 -H "X-API-Key: change-me"
```

Статусы: `pending`, `succeeded`, `failed`.

## Как устроено

- **Outbox.** Платеж и событие в `outbox` пишутся в одной транзакции. Poller забирает события через `FOR UPDATE SKIP LOCKED` и публикует в exchange `payments`.
- **Идемпотентность.** Повторный `POST` с тем же `Idempotency-Key` возвращает существующий платеж. Consumer не обрабатывает платеж повторно, если он уже не `pending`, и не шлет webhook второй раз (`webhook_sent_at`).
- **Retry.** При ошибке сообщение уходит в очередь задержки (`payments.new.retry.1` — 2 сек, `payments.new.retry.2` — 4 сек) и затем возвращается в `payments.new`.
- **DLQ.** После 3 неудачных попыток сообщение попадает в `payments.new.dlq` через exchange `payments.dlx`.
