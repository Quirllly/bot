"""added boost

Revision ID: 7a1b340cfb58
Revises: d3ee6c2d1cb4
Create Date: 2025-02-24 00:41:13.213303

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7a1b340cfb58"
down_revision: Union[str, None] = "d3ee6c2d1cb4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("boost", sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "boost")
    # ### end Alembic commands ###
