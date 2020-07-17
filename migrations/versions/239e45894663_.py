"""empty message

Revision ID: 239e45894663
Revises: 6e2da0b178a0
Create Date: 2020-07-14 05:19:44.813780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '239e45894663'
down_revision = '6e2da0b178a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('num_upcoming_shows', sa.Integer(), nullable=True))
    op.drop_column('Venue', 'num_upcoming_shows')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('num_upcoming_shows', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'num_upcoming_shows')
    # ### end Alembic commands ###