"""empty message

Revision ID: 92c2603274d9
Revises: 3ccbf8f3755a
Create Date: 2019-09-06 15:08:31.926479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92c2603274d9'
down_revision = '3ccbf8f3755a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('is_todos_done', 'todos_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('is_todos_done', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('is_todos_done', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('is_todos_done', 'todos_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
