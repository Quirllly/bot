"""fix_withdraw_requests_pk

Revision ID: 97d9c4a813c3
Revises: db200679cb7b
Create Date: 2025-03-07 16:25:12.104615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97d9c4a813c3'
down_revision: Union[str, None] = 'db200679cb7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table('withdrawl_requests',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('gift_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        # Добавьте это для явного указания отсутствия уникальности
        sa.UniqueConstraint('id', name='withdrawl_requests_pkey')  
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('withdrawl_requests')
    # ### end Alembic commands ###
