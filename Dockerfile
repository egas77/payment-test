FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --no-cache-dir "poetry==2.4.1"

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root && rm -rf /root/.cache/pypoetry

COPY alembic.ini main.py ./
COPY migrations ./migrations
COPY internal ./internal

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
