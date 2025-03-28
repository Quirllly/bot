"""Add last_daily_bonus column

Revision ID: d8b79ecee3fc
Revises: 21b36758e53c
Create Date: 2025-03-05 20:09:25.487634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8b79ecee3fc'
down_revision: Union[str, None] = '21b36758e53c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_daily_bonus', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_daily_bonus')
    # ### end Alembic commands ###
