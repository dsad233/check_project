"""local_rds_v4

Revision ID: f4e95a022ad0
Revises: f1241103d37d
Create Date: 2024-10-29 10:11:11.052855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = 'f4e95a022ad0'
down_revision: Union[str, None] = 'f1241103d37d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def create_table_safe(table_name: str, *args, **kwargs) -> None:
   try:
       op.create_table(table_name, *args, **kwargs)
   except Exception as e:
       print(f"{table_name} 테이블 생성 스킵: {e}")

def drop_table_safe(table_name: str) -> None:
   try:
       op.drop_table(table_name)
   except Exception as e:
       print(f"{table_name} 테이블 삭제 스킵: {e}")

def add_column_safe(table_name: str, column: sa.Column) -> None:
   try:
       op.add_column(table_name, column)
   except Exception as e:
       print(f"{table_name}의 {column.name} 컬럼 추가 스킵: {e}")

def drop_column_safe(table_name: str, column_name: str) -> None:
   try:
       op.drop_column(table_name, column_name)
   except Exception as e:
       print(f"{table_name}의 {column_name} 컬럼 삭제 스킵: {e}")

def upgrade() -> None:
   # ### commands auto generated by Alembic - please adjust! ###
   create_table_safe('parttimer_policies',
       sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
       sa.Column('branch_id', sa.Integer(), nullable=False),
       sa.Column('weekday_base_salary', sa.Boolean(), nullable=True),
       sa.Column('remote_base_salary', sa.Boolean(), nullable=True),
       sa.Column('annual_leave_allowance', sa.Boolean(), nullable=True),
       sa.Column('overtime_allowance', sa.Boolean(), nullable=True),
       sa.Column('holiday_work_allowance', sa.Boolean(), nullable=True),
       sa.Column('created_at', sa.DateTime(), nullable=True),
       sa.Column('updated_at', sa.DateTime(), nullable=True),
       sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
       sa.PrimaryKeyConstraint('id')
   )

   create_table_safe('salary_templates_policies',
       sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
       sa.Column('branch_id', sa.Integer(), nullable=False),
       sa.Column('part_id', sa.Integer(), nullable=False),
       sa.Column('unused_annual_leave_allowance', sa.Boolean(), nullable=True),
       sa.Column('additional_overtime_allowance', sa.Boolean(), nullable=True),
       sa.Column('additional_holiday_allowance', sa.Boolean(), nullable=True),
       sa.Column('annual_leave_deduction', sa.Boolean(), nullable=True),
       sa.Column('attendance_deduction', sa.Boolean(), nullable=True),
       sa.Column('created_at', sa.DateTime(), nullable=True),
       sa.Column('updated_at', sa.DateTime(), nullable=True),
       sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
       sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
       sa.PrimaryKeyConstraint('id'),
       sa.UniqueConstraint('part_id')
   )

   add_column_safe('allowance_policies', 
       sa.Column('payment_day', sa.Integer(), nullable=False))
   add_column_safe('allowance_policies', 
       sa.Column('base_salary', sa.Boolean(), nullable=True))
   # ### end Alembic commands ###


def downgrade() -> None:
   # ### commands auto generated by Alembic - please adjust! ###
   drop_column_safe('allowance_policies', 'base_salary')
   drop_column_safe('allowance_policies', 'payment_day')
   drop_table_safe('salary_templates_policies')
   drop_table_safe('parttimer_policies')
   # ### end Alembic commands ###