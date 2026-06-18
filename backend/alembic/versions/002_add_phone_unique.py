"""add unique constraint on customer phone_number

Revision ID: 002
Revises: 001
Create Date: 2026-06-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_customers_phone_number", "customers", ["phone_number"])


def downgrade() -> None:
    op.drop_constraint("uq_customers_phone_number", "customers", type_="unique")
