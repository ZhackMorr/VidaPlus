"""Adiciona a tabela de paciente

Revision ID: 0b9789995081
Revises: 54e7fe526cd5
Create Date: 2025-05-15 20:36:34.356569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b9789995081'
down_revision = '54e7fe526cd5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('paciente',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('data_nascimento', sa.String(length=10), nullable=False),
    sa.Column('cpf', sa.String(length=14), nullable=False),
    sa.Column('endereco', sa.String(length=200), nullable=True),
    sa.Column('telefone', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cpf')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('paciente')
    # ### end Alembic commands ###
