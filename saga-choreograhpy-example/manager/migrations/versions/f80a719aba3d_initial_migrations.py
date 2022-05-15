"""Initial migrations

Revision ID: f80a719aba3d
Revises: 
Create Date: 2022-05-15 05:15:17.686011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f80a719aba3d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('booking_request',
    sa.Column('booking_id', sa.String(), nullable=False),
    sa.Column('approved', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('booking_id'),
    schema='manager_schema'
    )
    op.create_index(op.f('ix_manager_schema_booking_request_booking_id'), 'booking_request', ['booking_id'], unique=True, schema='manager_schema')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_manager_schema_booking_request_booking_id'), table_name='booking_request', schema='manager_schema')
    op.drop_table('booking_request', schema='manager_schema')
    # ### end Alembic commands ###
