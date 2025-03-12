"""fix_withdraw_requests_pk

Revision ID: 26ae3c411f36
Revises: f4ee41e6a209
Create Date: 2025-03-10 20:42:48.278636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26ae3c411f36'
down_revision: Union[str, None] = 'f4ee41e6a209'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('tasks_order_key', 'tasks', type_='unique')
    op.drop_column('tasks', 'order')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('order', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_unique_constraint('tasks_order_key', 'tasks', ['order'])
    # ### end Alembic commands ###
