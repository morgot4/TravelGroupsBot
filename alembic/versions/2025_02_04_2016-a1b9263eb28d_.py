"""empty message

Revision ID: a1b9263eb28d
Revises: c6ddcfa29604
Create Date: 2025-02-04 20:16:47.559217

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b9263eb28d"
down_revision: Union[str, None] = "c6ddcfa29604"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "marks",
        "captain_telegram_id",
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "marks",
        "captain_telegram_id",
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=True,
    )
    # ### end Alembic commands ###
