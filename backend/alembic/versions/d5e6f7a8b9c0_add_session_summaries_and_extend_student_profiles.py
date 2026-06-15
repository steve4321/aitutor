"""add_session_summaries_and_extend_student_profiles

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-06-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd5e6f7a8b9c0'
down_revision = 'c4d5e6f7a8b9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'session_summaries',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('session_id', sa.Uuid(), sa.ForeignKey('learning_sessions.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('student_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('summary_text', sa.Text(), nullable=False),
        sa.Column('topics_discussed', sa.JSON(), nullable=True),
        sa.Column('knowledge_points_touched', sa.JSON(), nullable=True),
        sa.Column('mastery_changes', sa.JSON(), nullable=True),
        sa.Column('interaction_style', sa.JSON(), nullable=True),
        sa.Column('sentiment', sa.String(20), nullable=True),
        sa.Column('pending_items', sa.JSON(), nullable=True),
        sa.Column('model_used', sa.String(50), nullable=True),
        sa.Column('session_duration_min', sa.Integer(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_session_summaries_student_id', 'session_summaries', ['student_id'])

    op.add_column('student_profiles', sa.Column('learning_style', sa.String(30), nullable=True))
    op.add_column('student_profiles', sa.Column('interaction_pattern', sa.JSON(), nullable=True))
    op.add_column('student_profiles', sa.Column('emotional_trend', sa.JSON(), nullable=True))
    op.add_column('student_profiles', sa.Column('pace_category', sa.String(20), nullable=True))
    op.add_column('student_profiles', sa.Column('session_count_total', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('student_profiles', sa.Column('last_memory_update', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('student_profiles', 'last_memory_update')
    op.drop_column('student_profiles', 'session_count_total')
    op.drop_column('student_profiles', 'pace_category')
    op.drop_column('student_profiles', 'emotional_trend')
    op.drop_column('student_profiles', 'interaction_pattern')
    op.drop_column('student_profiles', 'learning_style')
    op.drop_index('ix_session_summaries_student_id', table_name='session_summaries')
    op.drop_table('session_summaries')
