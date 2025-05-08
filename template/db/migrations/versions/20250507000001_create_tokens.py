"""20250507000001_create_tokens

Revision ID: 20250507000001_create_tokens
Revises: 20250507000000_create_users
Create Date: 2025-05-07 05:22:16.018899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON

# revision identifiers, used by Alembic.
revision: str = '20250507000001_create_tokens'
down_revision: Union[str, None] = '20250507000000_create_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'tokens',
        sa.Column('id', sa.Integer(), nullable=False),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        sa.Column('user_id', sa.Integer(), nullable=False),

        sa.Column('token', sa.String(length=1023), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=63), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('location', JSON, nullable=True),
        sa.Column('device', JSON, nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    
    # Create indexes
    op.create_index('ix_tokens_user_id', 'tokens', ['user_id'])
    op.create_index('ix_tokens_token', 'tokens', ['token'])

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_tokens_token')
    op.drop_index('ix_tokens_user_id')
    op.drop_table('tokens')
