"""create_boards_table

Revision ID: 93e463003bf2
Revises: a4d591e16243
Create Date: 2025-09-05 01:32:32.077776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93e463003bf2'
down_revision = 'a4d591e16243'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create boards table
    op.create_table(
        'boards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=False, default=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_boards_id', 'boards', ['id'], unique=False)
    op.create_index('ix_boards_user_id', 'boards', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_boards_user_id', table_name='boards')
    op.drop_index('ix_boards_id', table_name='boards')
    op.drop_table('boards')
