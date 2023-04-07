"""create posts table

Revision ID: b0fefbfc9b0a
Revises: 
Create Date: 2021-12-24 18:44:32.168645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0fefbfc9b0a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable==False, primary_key=True, nullable=False))
    pass


def downgrade():
    op.drop_table('posts')
    pass
