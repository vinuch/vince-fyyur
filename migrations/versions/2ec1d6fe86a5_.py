"""empty message

Revision ID: 2ec1d6fe86a5
Revises: c3a1ead5241e
Create Date: 2020-07-14 16:33:43.460229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ec1d6fe86a5'
down_revision = 'c3a1ead5241e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('artist_image_link', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'artist_image_link')
    # ### end Alembic commands ###