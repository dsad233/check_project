"""create-hour-wage-template

Revision ID: 998d00b4929b
Revises: 0ada626cb05a
Create Date: 2024-10-16 20:43:24.945827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '998d00b4929b'
down_revision: Union[str, None] = '0ada626cb05a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hour_wage_templates',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('branch_id', sa.Integer(), nullable=False),
    sa.Column('part_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.Column('hour_wage', sa.Integer(), nullable=False),
    sa.Column('home_hour_wage', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_yn', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
    sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('branches', 'corporate_seal',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255),
               nullable=True)
    op.alter_column('branches', 'nameplate',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('branches', 'nameplate',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255),
               nullable=False)
    op.alter_column('branches', 'corporate_seal',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255),
               nullable=False)
    op.drop_table('hour_wage_templates')
    # ### end Alembic commands ###