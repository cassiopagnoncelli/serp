"""20250507000001_create_sessions

Revision ID: 20250507000001_create_sessions
Revises: 20250507000000_create_users
Create Date: 2025-05-07 05:22:16.018899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250507000001_create_sessions'
down_revision: Union[str, None] = '20250507000000_create_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        sa.Column('user_id', sa.Integer(), nullable=False),

        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=63), nullable=True),
        sa.Column('user_agent', sa.String(length=127), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('device', sa.String(length=255), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    
    # Create indexes
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('ix_sessions_token', 'sessions', ['token'])

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_sessions_token')
    op.drop_index('ix_sessions_user_id')
    op.drop_table('sessions')
