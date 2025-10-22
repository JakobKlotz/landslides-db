"""create lanslide view

Revision ID: 1fc1738312c6
Revises: 5854ae4edfbb
Create Date: 2025-10-22 08:38:41.203164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fc1738312c6'
down_revision: Union[str, Sequence[str], None] = '5854ae4edfbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE VIEW public.landslides_view AS
    SELECT
        l.id,
        l.date,
        l.report,
        l.report_source,
        l.report_url,
        c.name AS classification_name,
        l.source_id,
        s.name AS source_name,
        s.doi AS source_doi,
        l.geom
    FROM
        public.landslides l
    JOIN
        public.classification c ON l.classification_id = c.id
    JOIN
        public.sources s ON l.source_id = s.id;
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.landslides_view;")