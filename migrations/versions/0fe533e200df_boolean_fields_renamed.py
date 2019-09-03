"""boolean fields renamed

Revision ID: 0fe533e200df
Revises: 
Create Date: 2019-09-03 16:37:31.515665

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0fe533e200df'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('abstract',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pmid', sa.Integer(), nullable=True),
    sa.Column('abstract', mysql.LONGTEXT(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('is_locked', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('is_clear_to_label', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_abstract_pmid'), 'abstract', ['pmid'], unique=True)
    op.create_table('removed',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pmid', mysql.LONGTEXT(), nullable=True),
    sa.Column('abstract', mysql.LONGTEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('role', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_name'), 'user', ['name'], unique=False)
    op.create_table('response',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('len_of_neg', sa.Integer(), nullable=True),
    sa.Column('len_of_pos', sa.Integer(), nullable=True),
    sa.Column('len_of_clause', sa.Integer(), nullable=True),
    sa.Column('abstract_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['abstract_id'], ['abstract.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_abstracts',
    sa.Column('user.id', sa.Integer(), nullable=False),
    sa.Column('abstract.id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['abstract.id'], ['abstract.id'], ),
    sa.ForeignKeyConstraint(['user.id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user.id', 'abstract.id')
    )
    op.create_table('nsentence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sentence', mysql.LONGTEXT(), nullable=True),
    sa.Column('label', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('response_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['response_id'], ['response.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pclause',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('clause', mysql.LONGTEXT(), nullable=True),
    sa.Column('label', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('response_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['response_id'], ['response.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('psentence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sentence', mysql.LONGTEXT(), nullable=True),
    sa.Column('label', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('response_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['response_id'], ['response.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('psentence')
    op.drop_table('pclause')
    op.drop_table('nsentence')
    op.drop_table('user_abstracts')
    op.drop_table('response')
    op.drop_index(op.f('ix_user_name'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('removed')
    op.drop_index(op.f('ix_abstract_pmid'), table_name='abstract')
    op.drop_table('abstract')
    # ### end Alembic commands ###
