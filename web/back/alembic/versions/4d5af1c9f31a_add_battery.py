"""add battery

Revision ID: 4d5af1c9f31a
Revises: 56f8531dc8ad
Create Date: 2025-07-02 18:21:18.094529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d5af1c9f31a'
down_revision: Union[str, Sequence[str], None] = '56f8531dc8ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('device_data', sa.Column('battery', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('device_data', 'battery')
    # ### end Alembic commands ###
