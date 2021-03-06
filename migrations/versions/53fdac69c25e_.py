"""empty message

Revision ID: 53fdac69c25e
Revises: 
Create Date: 2017-07-30 15:47:04.749250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53fdac69c25e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'jenkins_job',
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('update_message', sa.Text(), nullable=True),
        sa.Column('failed_tests', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('jenkins_job')
    # ### end Alembic commands ###
