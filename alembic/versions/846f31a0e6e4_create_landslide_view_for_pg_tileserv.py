"""Create landslide view for pg_tileserv

Revision ID: 846f31a0e6e4
Revises: e2839191dbbe
Create Date: 2025-10-06 13:03:48.047058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '846f31a0e6e4'
down_revision: Union[str, Sequence[str], None] = 'e2839191dbbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE VIEW public.landslides_view AS
    SELECT
        l.id,
        l.date,
        l.source_id,
        l.report,
        c.name AS classification_name,
        s.name AS source_name,
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

