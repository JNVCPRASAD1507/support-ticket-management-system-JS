"""complete comments table

Revision ID: 74ac7b10b53a
Revises: a7defba4de43
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "74ac7b10b53a"
down_revision: Union[str, Sequence[str], None] = "a7defba4de43"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("comments")}
    indexes = {i["name"] for i in inspector.get_indexes("comments")}

    if "updated_at" not in columns:
        op.add_column(
            "comments",
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )

    if "ix_comments_ticket_id" not in indexes:
        op.create_index("ix_comments_ticket_id", "comments", ["ticket_id"], unique=False)
    if "ix_comments_user_id" not in indexes:
        op.create_index("ix_comments_user_id", "comments", ["user_id"], unique=False)

def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {i["name"] for i in inspector.get_indexes("comments")}
    if "ix_comments_user_id" in indexes:
        op.drop_index("ix_comments_user_id", table_name="comments")
    if "ix_comments_ticket_id" in indexes:
        op.drop_index("ix_comments_ticket_id", table_name="comments")
    columns = {c["name"] for c in inspector.get_columns("comments")}
    if "updated_at" in columns:
        op.drop_column("comments", "updated_at")
