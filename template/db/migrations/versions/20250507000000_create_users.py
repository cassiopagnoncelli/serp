"""empty message

Revision ID: 20250507000000_create_users
Revises: 
Create Date: 2025-05-07 03:35:17.856255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250507000000_create_users'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=255), nullable=False),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        sa.Column('account_id', sa.String(length=255), nullable=True),

        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('enc_password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=255), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('email')
    )
    
    # Create indexes
    op.create_index('ix_users_uuid', 'users', ['uuid'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_status', 'users', ['status'])
    op.create_index('ix_users_account_id', 'users', ['account_id'])

def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_users_account_id')
    op.drop_index('ix_users_status')
    op.drop_index('ix_users_email')
    op.drop_index('ix_users_uuid')
    op.drop_table('users')
