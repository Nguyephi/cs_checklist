"""empty message

Revision ID: c28d88f644a5
Revises: 92c2603274d9
Create Date: 2019-09-06 16:35:13.739653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c28d88f644a5'
down_revision = '92c2603274d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sub_todos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subTask', sa.String(), nullable=True),
    sa.Column('todo_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['todo_id'], ['todos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('todos', sa.Column('task', sa.String(length=500), nullable=True))
    op.drop_column('todos', 'description')
    op.drop_column('todos', 'title')
    op.drop_column('todos', 'isEdit')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todos', sa.Column('isEdit', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('todos', sa.Column('title', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('todos', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('todos', 'task')
    op.drop_table('sub_todos')
    # ### end Alembic commands ###
