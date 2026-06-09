"""initial_schema

Revision ID: c3f8a1b2d4e5
Revises:
Create Date: 2026-06-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3f8a1b2d4e5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- users (no FK dependencies) ---
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=True),
        sa.Column('phone', sa.String(20), unique=True, nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('name', name='uq_users_name'),
    )

    # --- student_profiles (depends on users) ---
    op.create_table(
        'student_profiles',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('grade_level', sa.SmallInteger(), nullable=True),
        sa.Column('target_exam', sa.String(20), nullable=True),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('daily_goal_minutes', sa.SmallInteger(), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=True),
        sa.Column('preferred_lang', sa.String(10), nullable=True),
        sa.Column('diagnostic_done', sa.Boolean(), nullable=True),
        sa.Column('diagnostic_result', sa.JSON(), nullable=True),
        sa.Column('xp_total', sa.Integer(), nullable=True),
        sa.Column('streak_days', sa.Integer(), nullable=True),
        sa.Column('longest_streak', sa.Integer(), nullable=True),
        sa.Column('last_active_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- parent_links (depends on users) ---
    op.create_table(
        'parent_links',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('parent_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relation', sa.String(20), nullable=True),
        sa.Column('notify_settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('parent_id', 'student_id', name='uq_parent_student'),
    )

    # --- courses (no FK dependencies) ---
    op.create_table(
        'courses',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=True),
        sa.Column('subject', sa.String(20), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_exam', sa.String(50), nullable=True),
        sa.Column('estimated_hours', sa.SmallInteger(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- units (depends on courses) ---
    op.create_table(
        'units',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('course_id', sa.Uuid(), sa.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code', sa.String(50), nullable=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.SmallInteger(), nullable=False),
        sa.Column('required_mastery', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- knowledge_points (no FK dependencies, self-referential via lesson_id deferred) ---
    op.create_table(
        'knowledge_points',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('subject', sa.String(20), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_en', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('pillar', sa.String(50), nullable=True),
        sa.Column('difficulty_level', sa.SmallInteger(), nullable=True),
        sa.Column('amc_level', sa.SmallInteger(), nullable=False),
        sa.Column('lesson_id', sa.Uuid(), sa.ForeignKey('lessons.id', ondelete='SET NULL', use_alter=True, name='fk_knowledge_points_lesson_id'), nullable=True),
        sa.Column('sort_order', sa.SmallInteger(), nullable=True),
        sa.Column('estimated_minutes', sa.SmallInteger(), nullable=True),
        sa.Column('amc_levels', sa.String(50), nullable=True),
        sa.Column('embedding', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- knowledge_dependencies (depends on knowledge_points) ---
    op.create_table(
        'knowledge_dependencies',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('prerequisite_id', sa.Uuid(), sa.ForeignKey('knowledge_points.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_id', sa.Uuid(), sa.ForeignKey('knowledge_points.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dependency_type', sa.String(20), nullable=True),
        sa.Column('strength', sa.SmallInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('prerequisite_id', 'target_id', name='uq_prerequisite_target'),
    )

    # --- lessons (depends on units, knowledge_points) ---
    op.create_table(
        'lessons',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('unit_id', sa.Uuid(), sa.ForeignKey('units.id', ondelete='CASCADE'), nullable=False),
        sa.Column('knowledge_point_id', sa.Uuid(), sa.ForeignKey('knowledge_points.id', ondelete='SET NULL'), nullable=True),
        sa.Column('code', sa.String(50), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('lesson_type', sa.String(30), nullable=True),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('estimated_minutes', sa.SmallInteger(), nullable=True),
        sa.Column('sort_order', sa.SmallInteger(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- problems (no FK dependencies) ---
    op.create_table(
        'problems',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('source_year', sa.SmallInteger(), nullable=True),
        sa.Column('source_code', sa.String(50), nullable=True),
        sa.Column('subject', sa.String(20), nullable=False),
        sa.Column('format', sa.String(30), nullable=False),
        sa.Column('question_markdown', sa.Text(), nullable=False),
        sa.Column('question_data', sa.JSON(), nullable=True),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=True),
        sa.Column('knowledge_point_ids', sa.JSON(), nullable=True),
        sa.Column('difficulty', sa.SmallInteger(), nullable=True),
        sa.Column('estimated_time_sec', sa.SmallInteger(), nullable=True),
        sa.Column('hints', sa.JSON(), nullable=True),
        sa.Column('misconceptions', sa.JSON(), nullable=True),
        sa.Column('step_decomposition', sa.JSON(), nullable=True),
        sa.Column('times_attempted', sa.Integer(), nullable=True),
        sa.Column('times_correct', sa.Integer(), nullable=True),
        sa.Column('avg_time_sec', sa.SmallInteger(), nullable=True),
        sa.Column('embedding', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_problems_subject_difficulty', 'problems', ['subject', 'difficulty'])

    # --- problem_solutions (depends on problems) ---
    op.create_table(
        'problem_solutions',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('problem_id', sa.Uuid(), sa.ForeignKey('problems.id', ondelete='CASCADE'), nullable=False),
        sa.Column('method_name', sa.String(100), nullable=True),
        sa.Column('solution_markdown', sa.Text(), nullable=False),
        sa.Column('key_insight', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.SmallInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- knowledge_states (depends on users, knowledge_points) ---
    op.create_table(
        'knowledge_states',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('student_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('knowledge_point_id', sa.Uuid(), sa.ForeignKey('knowledge_points.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mastery', sa.Float(), nullable=True),
        sa.Column('mastery_level', sa.String(20), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=True),
        sa.Column('correct', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.Float(), nullable=True),
        sa.Column('stability', sa.Float(), nullable=True),
        sa.Column('retrievability', sa.Float(), nullable=True),
        sa.Column('next_review', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_review', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('lapse_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('student_id', 'knowledge_point_id', name='uq_student_kp'),
    )
    op.create_index('ix_ks_student_id', 'knowledge_states', ['student_id'])
    op.create_index('ix_ks_knowledge_point_id', 'knowledge_states', ['knowledge_point_id'])

    # --- learning_sessions (depends on users, knowledge_points, lessons) ---
    op.create_table(
        'learning_sessions',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('student_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_type', sa.String(30), nullable=False),
        sa.Column('subject', sa.String(20), nullable=False),
        sa.Column('knowledge_point_id', sa.Uuid(), sa.ForeignKey('knowledge_points.id', ondelete='SET NULL'), nullable=True),
        sa.Column('lesson_id', sa.Uuid(), sa.ForeignKey('lessons.id', ondelete='SET NULL'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_sec', sa.Integer(), nullable=True),
        sa.Column('problems_total', sa.SmallInteger(), nullable=True),
        sa.Column('problems_correct', sa.SmallInteger(), nullable=True),
        sa.Column('score_pct', sa.Float(), nullable=True),
        sa.Column('xp_earned', sa.Integer(), nullable=True),
        sa.Column('checkpoint_id', sa.String(100), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_ls_student_id', 'learning_sessions', ['student_id'])

    # --- messages (depends on learning_sessions) ---
    op.create_table(
        'messages',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('session_id', sa.Uuid(), sa.ForeignKey('learning_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('media', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- student_attempts (depends on learning_sessions, users, problems) ---
    op.create_table(
        'student_attempts',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('session_id', sa.Uuid(), sa.ForeignKey('learning_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', sa.Uuid(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('problem_id', sa.Uuid(), sa.ForeignKey('problems.id', ondelete='CASCADE'), nullable=False),
        sa.Column('answer', sa.Text(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('time_spent_sec', sa.Integer(), nullable=True),
        sa.Column('hint_level_used', sa.SmallInteger(), nullable=True),
        sa.Column('error_type', sa.String(50), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('attempt_number', sa.SmallInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_sa_student_id', 'student_attempts', ['student_id'])
    op.create_index('ix_sa_session_id', 'student_attempts', ['session_id'])
    op.create_index('ix_sa_problem_id', 'student_attempts', ['problem_id'])

    # --- enrollments (depends on users, courses) ---
    op.create_table(
        'enrollments',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('user_id', sa.Uuid(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('course_id', sa.Uuid(), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('progress', sa.SmallInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'course_id', name='uq_enrollment_user_course'),
    )
    op.create_index('ix_enrollments_user_active', 'enrollments', ['user_id', 'is_active'])


def downgrade() -> None:
    op.drop_index('ix_enrollments_user_active', table_name='enrollments')
    op.drop_table('enrollments')

    op.drop_index('ix_sa_problem_id', table_name='student_attempts')
    op.drop_index('ix_sa_session_id', table_name='student_attempts')
    op.drop_index('ix_sa_student_id', table_name='student_attempts')
    op.drop_table('student_attempts')

    op.drop_table('messages')

    op.drop_index('ix_ls_student_id', table_name='learning_sessions')
    op.drop_table('learning_sessions')

    op.drop_index('ix_ks_knowledge_point_id', table_name='knowledge_states')
    op.drop_index('ix_ks_student_id', table_name='knowledge_states')
    op.drop_table('knowledge_states')

    op.drop_table('problem_solutions')

    op.drop_index('ix_problems_subject_difficulty', table_name='problems')
    op.drop_table('problems')

    op.drop_table('lessons')

    op.drop_table('knowledge_dependencies')
    op.drop_table('knowledge_points')

    op.drop_table('units')
    op.drop_table('courses')

    op.drop_table('parent_links')
    op.drop_table('student_profiles')
    op.drop_table('users')
