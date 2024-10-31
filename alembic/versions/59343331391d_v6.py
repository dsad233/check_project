"""v6

Revision ID: 59343331391d
Revises: 97a5d852086d
Create Date: 2024-10-31 09:47:15.919733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59343331391d'
down_revision: Union[str, None] = '97a5d852086d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('work_contract_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('work_contract_id', sa.Integer(), nullable=True),
    sa.Column('change_reason', sa.Text(), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_yn', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['work_contract_id'], ['work_contract.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('contract', sa.Column('work_contract_id', sa.Integer(), nullable=False))
    op.add_column('contract', sa.Column('modusign_id', sa.String(length=255), nullable=True))
    op.add_column('contract', sa.Column('contract_url', sa.String(length=255), nullable=False))
    op.add_column('contract', sa.Column('contract_status', sa.Enum('PENDING', 'APPROVE', 'REJECT', 'CANCEL', name='contractstatus'), nullable=False))
    op.add_column('contract', sa.Column('deleted_yn', sa.String(length=1), nullable=True))
    op.create_unique_constraint(None, 'contract', ['contract_url'])
    op.create_unique_constraint(None, 'contract', ['modusign_id'])
    op.create_foreign_key(None, 'contract', 'work_contract', ['work_contract_id'], ['id'])
    op.drop_column('contract', 'start_at')
    op.drop_column('contract', 'expired_at')
    op.add_column('work_contract', sa.Column('contract_creation_date', sa.Date(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('work_contract', 'contract_creation_date')
    op.add_column('contract', sa.Column('expired_at', sa.DATE(), nullable=True))
    op.add_column('contract', sa.Column('start_at', sa.DATE(), nullable=False))
    op.drop_constraint(None, 'contract', type_='foreignkey')
    op.drop_constraint(None, 'contract', type_='unique')
    op.drop_constraint(None, 'contract', type_='unique')
    op.drop_column('contract', 'deleted_yn')
    op.drop_column('contract', 'contract_status')
    op.drop_column('contract', 'contract_url')
    op.drop_column('contract', 'modusign_id')
    op.drop_column('contract', 'work_contract_id')
    op.drop_table('work_contract_history')
    # ### end Alembic commands ###
