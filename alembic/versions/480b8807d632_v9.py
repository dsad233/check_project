"""v9

Revision ID: 480b8807d632
Revises: f135e242650d
Create Date: 2024-10-31 20:53:51.940724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '480b8807d632'
down_revision: Union[str, None] = 'f135e242650d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'connection_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('connection_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_connection_logs_id', 'connection_logs', ['id'])

def downgrade():
    op.drop_index('ix_connection_logs_id', 'connection_logs')
    op.drop_table('connection_logs')