"""create_user_salary

Revision ID: 091da39ca9b6
Revises: 998d00b4929b
Create Date: 2024-10-17 09:34:43.077775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '091da39ca9b6'
down_revision: Union[str, None] = '998d00b4929b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_salaries',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('branch_id', sa.Integer(), nullable=False),
    sa.Column('part_id', sa.Integer(), nullable=False),
    sa.Column('monthly_salary', sa.Float(), nullable=False),
    sa.Column('annual_salary', sa.Float(), nullable=False),
    sa.Column('hourly_wage', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_yn', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
    sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('users', 'gender',
               existing_type=mysql.ENUM('남자', '여자', collation='utf8mb4_unicode_ci'),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'gender',
               existing_type=mysql.ENUM('남자', '여자', collation='utf8mb4_unicode_ci'),
               nullable=True)
    op.drop_table('user_salaries')
    # ### end Alembic commands ###