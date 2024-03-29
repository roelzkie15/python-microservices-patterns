"""Add domain_uuid to Booking sqlalchemy model

Revision ID: 5ffab98ff42c
Revises: fa1e57d87087
Create Date: 2022-08-06 15:54:41.554612

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5ffab98ff42c"
down_revision = "fa1e57d87087"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("bookings", sa.Column("domain_uuid", sa.String(), nullable=False))
    op.create_unique_constraint(None, "bookings", ["domain_uuid"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "bookings", type_="unique")
    op.drop_column("bookings", "domain_uuid")
    # ### end Alembic commands ###
