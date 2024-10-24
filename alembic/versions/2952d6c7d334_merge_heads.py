"""merge heads

Revision ID: 2952d6c7d334
Revises: bbfd4bd27a3b, 5dbe36fa0061
Create Date: 2024-10-24 18:52:30.477164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2952d6c7d334'
down_revision: Union[str, None] = ('bbfd4bd27a3b', '5dbe36fa0061')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
