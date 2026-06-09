"""add_ket_tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-09 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ket_questions',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('skill', sa.String(20), nullable=False),
        sa.Column('level', sa.String(10), nullable=False, server_default='A2'),
        sa.Column('question_type', sa.String(30), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('audio_url', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('points', sa.Integer(), server_default='1', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_ket_questions_skill', 'ket_questions', ['skill'])

    op.create_table(
        'ket_writing_tasks',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('task_type', sa.String(20), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('word_limit_min', sa.Integer(), server_default='25', nullable=True),
        sa.Column('word_limit_max', sa.Integer(), server_default='50', nullable=True),
        sa.Column('sample_response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'ket_speaking_tasks',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('topic', sa.String(100), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('difficulty', sa.String(20), server_default='easy', nullable=False),
        sa.Column('expected_duration_sec', sa.Integer(), server_default='30', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('ket_speaking_tasks')
    op.drop_table('ket_writing_tasks')
    op.drop_index('ix_ket_questions_skill', table_name='ket_questions')
    op.drop_table('ket_questions')
