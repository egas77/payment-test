"""lowercase status values

Revision ID: f9ad2beb1fb6
Revises: ad2cbc08b040
Create Date: 2026-10-05 21:19:53.493304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9ad2beb1fb6'
down_revision: Union[str, Sequence[str], None] = 'ad2cbc08b040'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


STATUSES = {
    "payment_status": ["PENDING", "SUCCEEDED", "FAILED"],
    "outbox_status": ["PENDING", "PUBLISHED"],
}


def upgrade() -> None:
    """Upgrade schema."""
    for type_name, values in STATUSES.items():
        for value in values:
            op.execute(f"ALTER TYPE {type_name} RENAME VALUE '{value}' TO '{value.lower()}'")


def downgrade() -> None:
    """Downgrade schema."""
    for type_name, values in STATUSES.items():
        for value in values:
            op.execute(f"ALTER TYPE {type_name} RENAME VALUE '{value.lower()}' TO '{value}'")
