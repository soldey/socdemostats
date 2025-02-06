"""update_nullable_territory_id

Revision ID: 4b8fce1e29e7
Revises: e90c3e500d33
Create Date: 2025-02-06 11:22:48.941218

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = '4b8fce1e29e7'
down_revision = 'e90c3e500d33'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("detailed_indicator_values") as alter_table_detailed_indicators:
        alter_table_detailed_indicators.alter_column(
            "detailed_indicator_values", "territory_id", nullable=True
        )
    with op.batch_alter_table("aggregated_indicator_values") as alter_table_aggregated_indicators:
        alter_table_aggregated_indicators.alter_column(
            "aggregated_indicator_values", "territory_id", nullable=True
        )


def downgrade() -> None:
    pass
