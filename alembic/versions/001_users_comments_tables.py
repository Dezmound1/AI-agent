"""Таблицы users и comments (характер и настроение комментария).

Revision ID: 001
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()

    postgresql.ENUM(
        "formal",
        "casual",
        "emotional",
        "sarcastic",
        "technical",
        name="comment_character",
    ).create(bind, checkfirst=True)
    postgresql.ENUM(
        "positive",
        "neutral",
        "negative",
        "mixed",
        name="comment_sentiment",
    ).create(bind, checkfirst=True)

    character_col = postgresql.ENUM(
        "formal",
        "casual",
        "emotional",
        "sarcastic",
        "technical",
        name="comment_character",
        create_type=False,
    )
    sentiment_col = postgresql.ENUM(
        "positive",
        "neutral",
        "negative",
        "mixed",
        name="comment_sentiment",
        create_type=False,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("character", character_col, nullable=False),
        sa.Column("sentiment", sentiment_col, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_user_id"), "comments", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_comments_user_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    postgresql.ENUM(name="comment_sentiment").drop(bind, checkfirst=True)
    postgresql.ENUM(name="comment_character").drop(bind, checkfirst=True)
