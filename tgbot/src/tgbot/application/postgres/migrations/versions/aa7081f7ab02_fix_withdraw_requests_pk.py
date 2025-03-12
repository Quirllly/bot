"""fix_withdraw_requests_pk

Revision ID: aa7081f7ab02
Revises: 4b383dc9db0a
Create Date: 2025-03-10 15:34:58.040459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa7081f7ab02'
down_revision: Union[str, None] = '4b383dc9db0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_task_data', sa.Column('completed_tasks', sa.JSON(), nullable=True))
    op.drop_constraint('user_task_data_task_id_fkey', 'user_task_data', type_='foreignkey')
    op.drop_column('user_task_data', 'task_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_task_data', sa.Column('task_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('user_task_data_task_id_fkey', 'user_task_data', 'tasks', ['task_id'], ['id'], ondelete='CASCADE')
    op.drop_column('user_task_data', 'completed_tasks')
    # ### end Alembic commands ###
