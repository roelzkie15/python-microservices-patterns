"""Initial migration

Revision ID: 9201fb72ddb9
Revises: 
Create Date: 2022-08-07 16:03:30.313387

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9201fb72ddb9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "parking_slots",
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="available", nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
    )
    with op.batch_alter_table("parking_slots", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_parking_slots_uuid"), ["uuid"], unique=True
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("parking_slots", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_parking_slots_uuid"))

    op.drop_table("parking_slots")
    # ### end Alembic commands ###
