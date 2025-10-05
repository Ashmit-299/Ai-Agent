"""merge conflicting heads

Revision ID: 33ae1ae5b5a6
Revises: 004, postgres_only_fixed
Create Date: 2025-10-05 10:02:00.997687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33ae1ae5b5a6'
down_revision: Union[str, Sequence[str], None] = ('004', 'postgres_only_fixed')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
