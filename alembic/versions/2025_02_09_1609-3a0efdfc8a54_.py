"""empty message

Revision ID: 3a0efdfc8a54
Revises: 9a6c15c176b5
Create Date: 2025-02-09 16:09:34.767115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a0efdfc8a54'
down_revision: Union[str, None] = '9a6c15c176b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('marks', sa.Column('last_point', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('marks', 'last_point')
    # ### end Alembic commands ###
