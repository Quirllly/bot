"""add_admins_table

Revision ID: 762a8b42bce3
Revises: d8b79ecee3fc
Create Date: 2025-03-05 20:32:13.223024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '52eedc624685'
down_revision: Union[str, None] = 'd8b79ecee3fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Создаем ENUM тип
    promocodetype = postgresql.ENUM(
        'simple', 
        'referral_based', 
        name='promocodetype'
    )
    promocodetype.create(op.get_bind())
    
    # Добавляем колонки с использованием созданного типа
    op.add_column('promocodes', sa.Column(
        'type', 
        promocodetype, 
        nullable=False,
        server_default='simple'  # Добавляем значение по умолчанию
    ))
    op.add_column('promocodes', sa.Column('required_referrals', sa.Integer(), nullable=True))
    op.add_column('promocodes', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('promocodes', sa.Column('expires_at', sa.DateTime(), nullable=False))
    
    # Удаляем значение по умолчанию после создания колонки
    op.alter_column('promocodes', 'type', server_default=None)

def downgrade() -> None:
    # Удаляем колонки
    op.drop_column('promocodes', 'expires_at')
    op.drop_column('promocodes', 'created_at')
    op.drop_column('promocodes', 'required_referrals')
    op.drop_column('promocodes', 'type')
    
    # Удаляем ENUM тип
    promocodetype = postgresql.ENUM(
        'simple', 
        'referral_based', 
        name='promocodetype'
    )
    promocodetype.drop(op.get_bind())
