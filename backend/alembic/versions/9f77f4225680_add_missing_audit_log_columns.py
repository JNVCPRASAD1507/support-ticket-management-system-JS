"""add missing audit log columns

Revision ID: 9f77f4225680
Revises: f1c932649bd1
Create Date: 2026-09-24 19:48:20.629962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f77f4225680'
down_revision: Union[str, Sequence[str], None] = 'f1c932649bd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# def upgrade() -> None:
#     """Upgrade schema."""
#     pass


# def downgrade() -> None:
#     """Downgrade schema."""
#     pass

def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column(
            "ip_address",
            sa.String(length=45),
            nullable=True,
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("audit_logs", "metadata")
    op.drop_column("audit_logs", "ip_address")
    
    
