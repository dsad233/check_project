"""v13

Revision ID: baa4ae945ce6
Revises: 68b9932ab102
Create Date: 2024-11-03 19:56:59.785424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'baa4ae945ce6'
down_revision: Union[str, None] = '68b9932ab102'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contract_info',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('manager_id', sa.Integer(), nullable=False),
    sa.Column('part_id', sa.Integer(), nullable=False),
    sa.Column('hire_date', sa.Date(), nullable=False),
    sa.Column('resignation_date', sa.Date(), nullable=True),
    sa.Column('contract_renewal_date', sa.Date(), nullable=True),
    sa.Column('job_title', sa.String(length=255), nullable=False),
    sa.Column('position', sa.String(length=255), nullable=False),
    sa.Column('employ_status', sa.Enum('정규직', '계약직', name='employ_status'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_yn', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contract_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contract_info_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('change_reason', sa.Text(), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_yn', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['contract_info_id'], ['contract_info.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('work_contract_history')
    op.add_column('contract', sa.Column('contract_info_id', sa.Integer(), nullable=False))
    op.add_column('contract', sa.Column('contract_type', sa.Enum('WORK', 'SALARY', 'PART_TIME', name='contract_type'), nullable=False))
    op.add_column('contract', sa.Column('contract_id', sa.Integer(), nullable=False))
    op.alter_column('contract', 'contract_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.alter_column('contract', 'contract_url',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.drop_constraint('contract_ibfk_3', 'contract', type_='foreignkey')
    op.drop_constraint('contract_ibfk_1', 'contract', type_='foreignkey')
    op.drop_constraint('contract_ibfk_4', 'contract', type_='foreignkey')
    op.drop_constraint('contract_ibfk_2', 'contract', type_='foreignkey')
    op.create_foreign_key(None, 'contract', 'contract_info', ['contract_info_id'], ['id'])
    op.drop_column('contract', 'contract_type_id')
    op.drop_column('contract', 'manager_id')
    op.drop_column('contract', 'user_id')
    op.drop_column('contract', 'work_contract_id')
    op.add_column('salary_contract', sa.Column('weekly_rest_hours', sa.Float(), nullable=False))
    op.drop_constraint('salary_contract_ibfk_1', 'salary_contract', type_='foreignkey')
    op.drop_column('salary_contract', 'user_id')
    op.drop_constraint('work_contract_ibfk_1', 'work_contract', type_='foreignkey')
    op.drop_column('work_contract', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('work_contract', sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('work_contract_ibfk_1', 'work_contract', 'users', ['user_id'], ['id'])
    op.add_column('salary_contract', sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('salary_contract_ibfk_1', 'salary_contract', 'users', ['user_id'], ['id'])
    op.drop_column('salary_contract', 'weekly_rest_hours')
    op.add_column('contract', sa.Column('work_contract_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('contract', sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('contract', sa.Column('manager_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('contract', sa.Column('contract_type_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'contract', type_='foreignkey')
    op.create_foreign_key('contract_ibfk_2', 'contract', 'users', ['manager_id'], ['id'])
    op.create_foreign_key('contract_ibfk_4', 'contract', 'work_contract', ['work_contract_id'], ['id'])
    op.create_foreign_key('contract_ibfk_1', 'contract', 'document_policies', ['contract_type_id'], ['id'])
    op.create_foreign_key('contract_ibfk_3', 'contract', 'users', ['user_id'], ['id'])
    op.alter_column('contract', 'contract_url',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.alter_column('contract', 'contract_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.drop_column('contract', 'contract_id')
    op.drop_column('contract', 'contract_type')
    op.drop_column('contract', 'contract_info_id')
    op.create_table('work_contract_history',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('work_contract_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('change_reason', mysql.TEXT(), nullable=True),
    sa.Column('note', mysql.TEXT(), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('deleted_yn', mysql.VARCHAR(length=1), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='work_contract_history_ibfk_1'),
    sa.ForeignKeyConstraint(['work_contract_id'], ['work_contract.id'], name='work_contract_history_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('contract_history')
    op.drop_table('contract_info')
    # ### end Alembic commands ###
