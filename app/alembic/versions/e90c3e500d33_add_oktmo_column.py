"""add_oktmo_column

Revision ID: e90c3e500d33
Revises: bd4f6a7f8981
Create Date: 2024-12-03 15:21:15.894590

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = 'e90c3e500d33'
down_revision = 'bd4f6a7f8981'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("detailed_indicator_values") as alter_table_detailed_indicators:
        alter_table_detailed_indicators.add_column(
            sa.Column(
                "oktmo",
                sa.Integer,
                nullable=True,
                default=None,
            )
        )
    with op.batch_alter_table("aggregated_indicator_values") as alter_table_aggregated_indicators:
        alter_table_aggregated_indicators.add_column(
            sa.Column(
                "oktmo",
                sa.Integer,
                nullable=True,
                default=None,
            )
        )


def downgrade() -> None:
    pass