"""empty message

Revision ID: 139c5861a582
Revises: 1ac73bf0fcd7
Create Date: 2015-12-27 16:07:46.306300

"""

# revision identifiers, used by Alembic.
revision = '139c5861a582'
down_revision = '1ac73bf0fcd7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('results', 'id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('results', sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False))
    ### end Alembic commands ###
