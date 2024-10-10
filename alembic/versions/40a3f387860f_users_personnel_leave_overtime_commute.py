"""users, personnel, leave, overtime, commute

Revision ID: 40a3f387860f
Revises: 
Create Date: 2024-10-10 21:56:09.141898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '40a3f387860f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('annual_leaves', 'deleted_yn',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.String(length=1),
               existing_nullable=True)
    op.alter_column('commutes', 'deleted_yn',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.String(length=1),
               existing_nullable=True)
    op.alter_column('overtimes', 'deleted_yn',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.String(length=1),
               existing_nullable=True)
    op.alter_column('personnel_records', 'deleted_yn',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.String(length=1),
               existing_nullable=True)
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('role', sa.Enum('MSO 최고권한', '최고관리자', '관리자', '사원', name='user_role'), nullable=True))
    op.add_column('users', sa.Column('part', sa.Enum('외래팀', '관리', '의사', '총괄 상담실장', '간호조무사', '코디네이터', '피부관리자', '상담실장', name='user_part'), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('deleted_yn', sa.String(length=1), nullable=True))
    op.alter_column('users', 'name',
               existing_type=mysql.VARCHAR(length=10),
               type_=sa.String(length=255),
               nullable=True)
    op.alter_column('users', 'password',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.drop_index('name', table_name='users')
    op.drop_column('users', 'createdAt')
    op.drop_column('users', 'isOpen')
    op.drop_column('users', 'updatedAt')
    op.drop_column('users', 'image')
    op.drop_column('users', 'deletedAt')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('deletedAt', mysql.DATETIME(), nullable=True))
    op.add_column('users', sa.Column('image', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('users', sa.Column('updatedAt', mysql.DATETIME(), nullable=True))
    op.add_column('users', sa.Column('isOpen', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('createdAt', mysql.DATETIME(), nullable=True))
    op.create_index('name', 'users', ['name'], unique=True)
    op.alter_column('users', 'password',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.alter_column('users', 'name',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=10),
               nullable=False)
    op.drop_column('users', 'deleted_yn')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'part')
    op.drop_column('users', 'role')
    op.drop_column('users', 'email')
    op.alter_column('personnel_records', 'deleted_yn',
               existing_type=sa.String(length=1),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('overtimes', 'deleted_yn',
               existing_type=sa.String(length=1),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('commutes', 'deleted_yn',
               existing_type=sa.String(length=1),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('annual_leaves', 'deleted_yn',
               existing_type=sa.String(length=1),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    # ### end Alembic commands ###
