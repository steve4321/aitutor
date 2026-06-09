"""add_embedding_vector_columns

Revision ID: a1b2c3d4e5f6
Revises: c3f8a1b2d4e5
Create Date: 2026-06-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'c3f8a1b2d4e5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        op.execute(
            "ALTER TABLE problems "
            "ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)"
        )
        op.execute(
            "ALTER TABLE knowledge_points "
            "ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)"
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE problems "
            "ALTER COLUMN embedding TYPE text USING embedding::text"
        )
        op.execute(
            "ALTER TABLE knowledge_points "
            "ALTER COLUMN embedding TYPE text USING embedding::text"
        )
