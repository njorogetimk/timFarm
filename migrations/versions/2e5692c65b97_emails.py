"""Emails

Revision ID: 2e5692c65b97
Revises: 8691ae9b02f0
Create Date: 2019-07-02 08:48:12.553763

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e5692c65b97'
down_revision = '8691ae9b02f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('farm', sa.Column('confirmed', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmed')
    op.drop_column('farm', 'confirmed')
    # ### end Alembic commands ###
