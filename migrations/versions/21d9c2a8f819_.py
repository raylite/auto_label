"""empty message

Revision ID: 21d9c2a8f819
Revises: 26520ecda310
Create Date: 2019-07-19 15:44:39.774024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21d9c2a8f819'
down_revision = '26520ecda310'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('authenticated', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'authenticated')
    # ### end Alembic commands ###