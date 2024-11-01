"""v8

Revision ID: f135e242650d
Revises: 125252945859
Create Date: 2024-10-31 17:16:43.145156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'f135e242650d'
down_revision: Union[str, None] = '125252945859'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('break_times',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('work_policy_id', sa.Integer(), nullable=False),
    sa.Column('is_doctor', sa.Boolean(), nullable=True),
    sa.Column('break_type', sa.String(length=10), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('end_time', sa.Time(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['work_policy_id'], ['work_policies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('work_schedules',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('work_policy_id', sa.Integer(), nullable=False),
    sa.Column('day_of_week', sa.Enum('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY', name='weekday'), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.Column('is_holiday', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['work_policy_id'], ['work_policies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('user_leaves_days', 'description')
    op.drop_column('user_leaves_days', 'total_decreased_days')
    op.drop_column('user_leaves_days', 'total_increased_days')
    op.alter_column('work_contract', 'deleted_yn',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.String(length=1),
               existing_nullable=True)
    op.drop_column('work_policies', 'saturday_end_time')
    op.drop_column('work_policies', 'common_dinner_end_time')
    op.drop_column('work_policies', 'weekday_is_holiday')
    op.drop_column('work_policies', 'weekday_end_time')
    op.drop_column('work_policies', 'doctor_lunch_end_time')
    op.drop_column('work_policies', 'doctor_dinner_end_time')
    op.drop_column('work_policies', 'doctor_lunch_start_time')
    op.drop_column('work_policies', 'common_lunch_end_time')
    op.drop_column('work_policies', 'common_dinner_start_time')
    op.drop_column('work_policies', 'sunday_start_time')
    op.drop_column('work_policies', 'saturday_is_holiday')
    op.drop_column('work_policies', 'doctor_dinner_start_time')
    op.drop_column('work_policies', 'sunday_is_holiday')
    op.drop_column('work_policies', 'saturday_start_time')
    op.drop_column('work_policies', 'weekday_start_time')
    op.drop_column('work_policies', 'common_lunch_start_time')
    op.drop_column('work_policies', 'sunday_end_time')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('work_policies', sa.Column('sunday_end_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('common_lunch_start_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('weekday_start_time', mysql.TIME(), nullable=False))
    op.add_column('work_policies', sa.Column('saturday_start_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('sunday_is_holiday', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('work_policies', sa.Column('doctor_dinner_start_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('saturday_is_holiday', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('work_policies', sa.Column('sunday_start_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('common_dinner_start_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('common_lunch_end_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('doctor_lunch_start_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('doctor_dinner_end_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('doctor_lunch_end_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('weekday_end_time', mysql.TIME(), nullable=False))
    op.add_column('work_policies', sa.Column('weekday_is_holiday', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('work_policies', sa.Column('common_dinner_end_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('saturday_end_time', mysql.TIME(), nullable=True))
    op.alter_column('work_contract', 'deleted_yn',
               existing_type=sa.String(length=1),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.add_column('user_leaves_days', sa.Column('total_increased_days', mysql.DECIMAL(precision=10, scale=2), nullable=False))
    op.add_column('user_leaves_days', sa.Column('total_decreased_days', mysql.DECIMAL(precision=10, scale=2), nullable=False))
    op.add_column('user_leaves_days', sa.Column('description', mysql.VARCHAR(length=255), nullable=True))
    op.drop_table('work_schedules')
    op.drop_table('break_times')
    # ### end Alembic commands ###
