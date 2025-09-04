"""fix_boards_updated_at_default

Revision ID: d05eeb6f3a0b
Revises: 93e463003bf2
Create Date: 2025-09-05 01:34:13.148832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd05eeb6f3a0b'
down_revision = '93e463003bf2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add default value to updated_at column
    op.alter_column('boards', 'updated_at', 
                   server_default=sa.text('now()'))


def downgrade() -> None:
    # Remove default value from updated_at column
    op.alter_column('boards', 'updated_at', 
                   server_default=None)
