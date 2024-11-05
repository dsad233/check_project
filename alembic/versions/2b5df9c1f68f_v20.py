"""v20

Revision ID: 2b5df9c1f68f
Revises: 25fc952e4b37
Create Date: 2024-11-05 13:52:10.645088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b5df9c1f68f'
down_revision: Union[str, None] = '25fc952e4b37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contract_info', sa.Column('activate_yn', sa.Enum('Y', 'N', name='activate_yn'), nullable=False))
    op.add_column('document_send_history', sa.Column('request_date', sa.Date(), nullable=False))
    op.add_column('document_send_history', sa.Column('request_reason', sa.String(length=255), nullable=False))
    op.add_column('document_send_history', sa.Column('deleted_yn', sa.String(length=1), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('document_send_history', 'deleted_yn')
    op.drop_column('document_send_history', 'request_reason')
    op.drop_column('document_send_history', 'request_date')
    op.drop_column('contract_info', 'activate_yn')
    # ### end Alembic commands ###