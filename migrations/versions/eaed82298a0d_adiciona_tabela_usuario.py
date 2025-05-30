"""Adiciona tabela usuario

Revision ID: eaed82298a0d
Revises: e31a3126906d
Create Date: 2025-05-18 14:28:16.904432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eaed82298a0d'
down_revision = 'e31a3126906d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usuario',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('senha_hash', sa.String(length=200), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=False),
    sa.Column('paciente_id', sa.Integer(), nullable=True),
    sa.Column('profissional_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['paciente_id'], ['paciente.id'], ),
    sa.ForeignKeyConstraint(['profissional_id'], ['profissional.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('usuario')
    # ### end Alembic commands ###
