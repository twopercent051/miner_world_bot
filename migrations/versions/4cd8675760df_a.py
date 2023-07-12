"""a

Revision ID: 4cd8675760df
Revises: 7b73fccf87c9
Create Date: 2023-07-12 13:15:47.802550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cd8675760df'
down_revision = '7b73fccf87c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tickets', sa.Column('reg_dtime', sa.TIMESTAMP(), server_default=sa.text("TIMEZONE('Asia/Irkutsk', CURRENT_TIMESTAMP)"), nullable=False))
    op.add_column('users', sa.Column('reg_dtime', sa.TIMESTAMP(), server_default=sa.text("TIMEZONE('Asia/Irkutsk', CURRENT_TIMESTAMP)"), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'reg_dtime')
    op.drop_column('tickets', 'reg_dtime')
    # ### end Alembic commands ###