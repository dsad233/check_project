"""modify_parts_create_leave_excluded

Revision ID: e3440c11d246
Revises: 930046fbc4de
Create Date: 2024-10-17 18:01:18.332712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3440c11d246'
down_revision: Union[str, None] = '930046fbc4de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('leave_excluded_parts',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('leave_category_id', sa.Integer(), nullable=False),
    sa.Column('part_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['leave_category_id'], ['leave_categories.id'], ),
    sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('closed_days', sa.Column('is_sunday', sa.Boolean(), nullable=True))
    op.add_column('parts', sa.Column('color', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('parts', 'color')
    op.drop_column('closed_days', 'is_sunday')
    op.drop_table('leave_excluded_parts')
    # ### end Alembic commands ###