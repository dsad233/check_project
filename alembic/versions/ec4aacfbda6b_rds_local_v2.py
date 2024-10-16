"""rds+local_v2

Revision ID: ec4aacfbda6b
Revises: 45056817e69a
Create Date: 2024-10-16 10:42:26.763985

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'ec4aacfbda6b'
down_revision: Union[str, None] = '45056817e69a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('overtimes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('applicant_id', sa.Integer(), nullable=False),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.Column('overtime_hours', sa.Enum('30', '60', '90', '120', name='overtime_hours_options'), nullable=False),
    sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='overtime_status'), nullable=False),
    sa.Column('application_date', sa.Date(), nullable=False),
    sa.Column('application_memo', sa.String(length=500), nullable=True),
    sa.Column('manager_memo', sa.String(length=500), nullable=True),
    sa.Column('processed_date', sa.Date(), nullable=True),
    sa.Column('is_approved', sa.String(length=1), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_yn', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['applicant_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('board_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_yn', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('allowance_policies', sa.Column('branch_id', sa.Integer(), nullable=False))
    op.add_column('allowance_policies', sa.Column('doctor_holiday_work_pay', sa.Integer(), nullable=False))
    op.add_column('allowance_policies', sa.Column('common_holiday_work_pay', sa.Integer(), nullable=False))
    op.drop_constraint('allowance_policies_ibfk_1', 'allowance_policies', type_='foreignkey')
    op.create_foreign_key(None, 'allowance_policies', 'branches', ['branch_id'], ['id'])
    op.drop_column('allowance_policies', 'part_id')
    op.add_column('auto_overtime_policies', sa.Column('top_manager_auto_applied', sa.Boolean(), nullable=True))
    op.add_column('auto_overtime_policies', sa.Column('manager_auto_applied', sa.Boolean(), nullable=True))
    op.add_column('auto_overtime_policies', sa.Column('employee_auto_applied', sa.Boolean(), nullable=True))
    op.drop_column('auto_overtime_policies', 'role')
    op.drop_column('auto_overtime_policies', 'is_auto_applied')
    op.add_column('leave_histories', sa.Column('branch_id', sa.Integer(), nullable=False))
    op.add_column('leave_histories', sa.Column('application_date', sa.Date(), nullable=False))
    op.add_column('leave_histories', sa.Column('approve_date', sa.Date(), nullable=True))
    op.add_column('leave_histories', sa.Column('applicant_description', sa.String(length=255), nullable=True))
    op.add_column('leave_histories', sa.Column('admin_description', sa.String(length=255), nullable=True))
    op.add_column('leave_histories', sa.Column('status', sa.Enum('확인중', '승인', '반려', name='leave_history_status'), nullable=False))
    op.drop_index('idx_leave_history_date', table_name='leave_histories')
    op.drop_index('uq_user_date', table_name='leave_histories')
    op.create_index('idx_leave_history_application_date', 'leave_histories', ['application_date'], unique=False)
    op.create_unique_constraint('uq_user_application_date', 'leave_histories', ['user_id', 'application_date'])
    op.create_foreign_key(None, 'leave_histories', 'branches', ['branch_id'], ['id'])
    op.drop_column('leave_histories', 'is_leave_of_absence')
    op.drop_column('leave_histories', 'description')
    op.drop_column('leave_histories', 'is_paid')
    op.drop_column('leave_histories', 'is_approved')
    op.drop_column('leave_histories', 'date')
    op.add_column('overtime_policies', sa.Column('doctor_ot_30', sa.Integer(), nullable=False))
    op.add_column('overtime_policies', sa.Column('doctor_ot_60', sa.Integer(), nullable=False))
    op.add_column('overtime_policies', sa.Column('doctor_ot_90', sa.Integer(), nullable=False))
    op.add_column('overtime_policies', sa.Column('doctor_ot_120', sa.Integer(), nullable=False))
    op.add_column('overtime_policies', sa.Column('common_ot_30', sa.Integer(), nullable=False))
    op.add_column('overtime_policies', sa.Column('common_ot_60', sa.Integer(), nullable=False))
    op.add_column('overtime_policies', sa.Column('common_ot_90', sa.Integer(), nullable=False))
    op.add_column('overtime_policies', sa.Column('common_ot_120', sa.Integer(), nullable=False))
    op.drop_column('overtime_policies', 'ot_60')
    op.drop_column('overtime_policies', 'ot_90')
    op.drop_column('overtime_policies', 'name')
    op.drop_column('overtime_policies', 'ot_120')
    op.drop_column('overtime_policies', 'ot_30')
    op.add_column('work_policies', sa.Column('branch_id', sa.Integer(), nullable=False))
    op.add_column('work_policies', sa.Column('doctor_lunch_start_time', sa.Time(), nullable=True))
    op.add_column('work_policies', sa.Column('doctor_lunch_end_time', sa.Time(), nullable=True))
    op.add_column('work_policies', sa.Column('doctor_dinner_start_time', sa.Time(), nullable=True))
    op.add_column('work_policies', sa.Column('doctor_dinner_end_time', sa.Time(), nullable=True))
    op.add_column('work_policies', sa.Column('common_lunch_start_time', sa.Time(), nullable=True))
    op.add_column('work_policies', sa.Column('common_lunch_end_time', sa.Time(), nullable=True))
    op.add_column('work_policies', sa.Column('common_dinner_start_time', sa.Time(), nullable=True))
    op.add_column('work_policies', sa.Column('common_dinner_end_time', sa.Time(), nullable=True))
    op.drop_constraint('work_policies_ibfk_1', 'work_policies', type_='foreignkey')
    op.create_foreign_key(None, 'work_policies', 'branches', ['branch_id'], ['id'])
    op.drop_column('work_policies', 'staff_break_end_time')
    op.drop_column('work_policies', 'part_id')
    op.drop_column('work_policies', 'staff_break_start_time')
    op.drop_column('work_policies', 'doctor_break_end_time')
    op.drop_column('work_policies', 'doctor_break_start_time')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('work_policies', sa.Column('doctor_break_start_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('doctor_break_end_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('staff_break_start_time', mysql.TIME(), nullable=True))
    op.add_column('work_policies', sa.Column('part_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('work_policies', sa.Column('staff_break_end_time', mysql.TIME(), nullable=True))
    op.drop_constraint(None, 'work_policies', type_='foreignkey')
    op.create_foreign_key('work_policies_ibfk_1', 'work_policies', 'parts', ['part_id'], ['id'])
    op.drop_column('work_policies', 'common_dinner_end_time')
    op.drop_column('work_policies', 'common_dinner_start_time')
    op.drop_column('work_policies', 'common_lunch_end_time')
    op.drop_column('work_policies', 'common_lunch_start_time')
    op.drop_column('work_policies', 'doctor_dinner_end_time')
    op.drop_column('work_policies', 'doctor_dinner_start_time')
    op.drop_column('work_policies', 'doctor_lunch_end_time')
    op.drop_column('work_policies', 'doctor_lunch_start_time')
    op.drop_column('work_policies', 'branch_id')
    op.add_column('overtime_policies', sa.Column('ot_30', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('overtime_policies', sa.Column('ot_120', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('overtime_policies', sa.Column('name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255), nullable=False))
    op.add_column('overtime_policies', sa.Column('ot_90', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('overtime_policies', sa.Column('ot_60', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('overtime_policies', 'common_ot_120')
    op.drop_column('overtime_policies', 'common_ot_90')
    op.drop_column('overtime_policies', 'common_ot_60')
    op.drop_column('overtime_policies', 'common_ot_30')
    op.drop_column('overtime_policies', 'doctor_ot_120')
    op.drop_column('overtime_policies', 'doctor_ot_90')
    op.drop_column('overtime_policies', 'doctor_ot_60')
    op.drop_column('overtime_policies', 'doctor_ot_30')
    op.add_column('leave_histories', sa.Column('date', sa.DATE(), nullable=False))
    op.add_column('leave_histories', sa.Column('is_approved', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('leave_histories', sa.Column('is_paid', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column('leave_histories', sa.Column('description', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255), nullable=True))
    op.add_column('leave_histories', sa.Column('is_leave_of_absence', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'leave_histories', type_='foreignkey')
    op.drop_constraint('uq_user_application_date', 'leave_histories', type_='unique')
    op.drop_index('idx_leave_history_application_date', table_name='leave_histories')
    op.create_index('uq_user_date', 'leave_histories', ['user_id', 'date'], unique=True)
    op.create_index('idx_leave_history_date', 'leave_histories', ['date'], unique=False)
    op.drop_column('leave_histories', 'status')
    op.drop_column('leave_histories', 'admin_description')
    op.drop_column('leave_histories', 'applicant_description')
    op.drop_column('leave_histories', 'approve_date')
    op.drop_column('leave_histories', 'application_date')
    op.drop_column('leave_histories', 'branch_id')
    op.add_column('auto_overtime_policies', sa.Column('is_auto_applied', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('auto_overtime_policies', sa.Column('role', mysql.ENUM('최고관리자', '관리자', collation='utf8mb4_unicode_ci'), nullable=False))
    op.drop_column('auto_overtime_policies', 'employee_auto_applied')
    op.drop_column('auto_overtime_policies', 'manager_auto_applied')
    op.drop_column('auto_overtime_policies', 'top_manager_auto_applied')
    op.add_column('allowance_policies', sa.Column('part_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'allowance_policies', type_='foreignkey')
    op.create_foreign_key('allowance_policies_ibfk_1', 'allowance_policies', 'parts', ['part_id'], ['id'])
    op.drop_column('allowance_policies', 'common_holiday_work_pay')
    op.drop_column('allowance_policies', 'doctor_holiday_work_pay')
    op.drop_column('allowance_policies', 'branch_id')
    op.drop_table('comments')
    op.drop_table('overtimes')
    # ### end Alembic commands ###