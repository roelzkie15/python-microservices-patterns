"""Add parking_space_uuid field

Revision ID: c41c4cfb8162
Revises: f96307a1d404
Create Date: 2022-05-21 17:43:15.585874

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c41c4cfb8162'
down_revision = 'f96307a1d404'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookings', sa.Column('description', sa.String(), nullable=True))
    op.add_column('bookings', sa.Column('parking_space_uuid', sa.String(), nullable=True))
    op.drop_column('bookings', 'desc')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookings', sa.Column('desc', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('bookings', 'parking_space_uuid')
    op.drop_column('bookings', 'description')
    # ### end Alembic commands ###