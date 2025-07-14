"""init users table

Revision ID: afe8331721f6
Revises:
Create Date: 2025-07-14 19:18:58.198307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afe8331721f6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('telegram_id', sa.String(), nullable=False),
                    sa.Column('subscription_type', sa.String(length=50), nullable=True),
                    sa.Column('subscription_end', sa.DateTime(), nullable=True),
                    sa.Column('request_count', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('telegram_id')
                    )

def downgrade():
    op.drop_table('users')
