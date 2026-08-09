"""Added default factory to AnalyticsJob model

Revision ID: 4f76ae0cf8b9
Revises: bde09c8746cc
Create Date: 2026-08-09 20:04:14.430570

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4f76ae0cf8b9'
down_revision: Union[str, Sequence[str], None] = 'bde09c8746cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'analytics_jobs',
        'result',
        existing_type=postgresql.JSONB(),
        server_default=sa.text("'{}'::jsonb"),
        existing_nullable=False
    )

def downgrade() -> None:
    op.alter_column(
        'analytics_jobs',
        'result',
        existing_type=postgresql.JSONB(),
        server_default=None,
        existing_nullable=False
    )
