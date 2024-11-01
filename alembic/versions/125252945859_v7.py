"""v7

Revision ID: 125252945859
Revises: 59343331391d
Create Date: 2024-10-31 15:32:00.776119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '125252945859'
down_revision: Union[str, None] = '59343331391d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   # ### commands auto generated by Alembic - please adjust! ###
   op.create_table('work_contract_break_time',
   sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
   sa.Column('work_contract_id', sa.Integer(), nullable=False),
   sa.Column('break_start_time', sa.Time(), nullable=False),
   sa.Column('break_end_time', sa.Time(), nullable=False),
   sa.Column('created_at', sa.DateTime(), nullable=True),
   sa.Column('updated_at', sa.DateTime(), nullable=True),
   sa.Column('deleted_yn', sa.String(length=1), nullable=True),
   sa.ForeignKeyConstraint(['work_contract_id'], ['work_contract.id'], ),
   sa.PrimaryKeyConstraint('id')
   )
   
   # leave_histories 테이블의 컬럼 존재 여부 확인 후 삭제
   conn = op.get_bind()
   inspector = inspect(conn)
   columns = inspector.get_columns('leave_histories')
   column_names = [col['name'] for col in columns]
   
   if 'manager_id' in column_names:
       op.drop_column('leave_histories', 'manager_id')
   if 'manager_name' in column_names:
       op.drop_column('leave_histories', 'manager_name')
       
   op.add_column('work_contract', sa.Column('deleted_yn', sa.Boolean(), nullable=True))
   op.drop_column('work_contract', 'break_end_time')
   op.drop_column('work_contract', 'saturday_is_rest')
   op.drop_column('work_contract', 'break_start_time')
   op.drop_column('work_contract', 'sunday_is_rest')
   op.drop_column('work_contract', 'weekly_is_rest')
   # ### end Alembic commands ###


def downgrade() -> None:
   # ### commands auto generated by Alembic - please adjust! ###
   op.add_column('work_contract', sa.Column('weekly_is_rest', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
   op.add_column('work_contract', sa.Column('sunday_is_rest', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
   op.add_column('work_contract', sa.Column('break_start_time', mysql.TIME(), nullable=True))
   op.add_column('work_contract', sa.Column('saturday_is_rest', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
   op.add_column('work_contract', sa.Column('break_end_time', mysql.TIME(), nullable=True))
   op.drop_column('work_contract', 'deleted_yn')
   op.add_column('leave_histories', sa.Column('manager_name', mysql.VARCHAR(length=10), nullable=True))
   op.add_column('leave_histories', sa.Column('manager_id', mysql.INTEGER(), autoincrement=False, nullable=True))
   op.drop_table('work_contract_break_time')
   # ### end Alembic commands ###