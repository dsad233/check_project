"""update Users field

Revision ID: 97a5d852086d
Revises: 8c82b2e1a98d
Create Date: 2024-10-30 19:30:20.136351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97a5d852086d'
down_revision: Union[str, None] = '8c82b2e1a98d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None 


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('en_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_foreigner', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('stay_start_date', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('sabbatical_start_date', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('sabbatical_end_date', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('position', sa.Enum('MSO 최고권한', '최고관리자', '통합관리자', '관리자', '사원', '퇴사자', '휴직자', '임시생성', name='user_position'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'position')
    op.drop_column('users', 'sabbatical_end_date')
    op.drop_column('users', 'sabbatical_start_date')
    op.drop_column('users', 'stay_start_date')
    op.drop_column('users', 'is_foreigner')
    op.drop_column('users', 'en_name')
    # ### end Alembic commands ###