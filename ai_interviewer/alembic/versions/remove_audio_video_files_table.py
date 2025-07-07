"""Remove audio_video_files table for real-time streaming

Revision ID: remove_audio_video_files
Revises: 1184bcb8a972
Create Date: 2025-07-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_audio_video_files'
down_revision = '1184bcb8a972'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the audio_video_files table if it exists
    try:
        op.drop_index(op.f('ix_audio_video_files_id'), table_name='audio_video_files')
        op.drop_table('audio_video_files')
    except:
        # Table might not exist if it was never created
        pass


def downgrade() -> None:
    # Recreate the audio_video_files table if needed
    op.create_table('audio_video_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('interview_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('file_type', sa.String(), nullable=False),
    sa.Column('file_format', sa.String(), nullable=True),
    sa.Column('file_size_bytes', sa.Integer(), nullable=True),
    sa.Column('duration_seconds', sa.Float(), nullable=True),
    sa.Column('gcs_bucket', sa.String(), nullable=True),
    sa.Column('gcs_object_path', sa.String(), nullable=True),
    sa.Column('gcs_url', sa.String(), nullable=True),
    sa.Column('upload_status', sa.String(), nullable=True),
    sa.Column('transcription_status', sa.String(), nullable=True),
    sa.Column('transcription_text', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['interview_questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audio_video_files_id'), 'audio_video_files', ['id'], unique=False)
