"""add_missing_indexes

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-06-16 11:00:00.000000

"""
from alembic import op


revision = 'f7a8b9c0d1e2'
down_revision = 'e6f7a8b9c0d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index('ix_ls_student_started', 'learning_sessions', ['student_id', 'started_at'])
    op.create_index('ix_ls_knowledge_point_id', 'learning_sessions', ['knowledge_point_id'])
    op.create_index('ix_ls_lesson_id', 'learning_sessions', ['lesson_id'])

    op.create_index('ix_ks_next_review', 'knowledge_states', ['student_id', 'next_review'])
    op.create_index('ix_ks_mastery', 'knowledge_states', ['student_id', 'mastery'])

    op.create_index('ix_msg_session_id', 'messages', ['session_id'])


def downgrade() -> None:
    op.drop_index('ix_msg_session_id', table_name='messages')

    op.drop_index('ix_ks_mastery', table_name='knowledge_states')
    op.drop_index('ix_ks_next_review', table_name='knowledge_states')

    op.drop_index('ix_ls_lesson_id', table_name='learning_sessions')
    op.drop_index('ix_ls_knowledge_point_id', table_name='learning_sessions')
    op.drop_index('ix_ls_student_started', table_name='learning_sessions')
