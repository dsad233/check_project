"""create auto leave grant, approval

Revision ID: 0b20af972bae
Revises: e3440c11d246
Create Date: 2024-10-21 10:06:24.962743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '0b20af972bae'
down_revision: Union[str, None] = 'e3440c11d246'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auto_overtime_policies', sa.Column('top_auto_applied', sa.Boolean(), nullable=True))
    op.add_column('auto_overtime_policies', sa.Column('total_auto_applied', sa.Boolean(), nullable=True))
    op.add_column('auto_overtime_policies', sa.Column('part_auto_applied', sa.Boolean(), nullable=True))
    op.drop_column('auto_overtime_policies', 'manager_auto_applied')
    op.drop_column('auto_overtime_policies', 'employee_auto_applied')
    op.drop_column('auto_overtime_policies', 'top_manager_auto_applied')
    op.drop_column('closed_days', 'is_sunday')
    op.drop_column('leave_categories', 'is_leave_of_absence')
    op.add_column('parts', sa.Column('auto_annual_leave_grant', sa.Enum('수동부여', '회계기준 부여', '입사일 기준 부여', '조건별 부여', name='part_auto_annual_leave_grant'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('parts', 'auto_annual_leave_grant')
    op.add_column('leave_categories', sa.Column('is_leave_of_absence', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('closed_days', sa.Column('is_sunday', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('auto_overtime_policies', sa.Column('top_manager_auto_applied', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('auto_overtime_policies', sa.Column('employee_auto_applied', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('auto_overtime_policies', sa.Column('manager_auto_applied', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_column('auto_overtime_policies', 'part_auto_applied')
    op.drop_column('auto_overtime_policies', 'total_auto_applied')
    op.drop_column('auto_overtime_policies', 'top_auto_applied')
    # ### end Alembic commands ###
