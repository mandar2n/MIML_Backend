"""Add reaction column to Song

Revision ID: 348fcb6d836f
Revises: 0fb58acf759c
Create Date: 2024-11-13 18:21:27.831952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '348fcb6d836f'
down_revision: Union[str, None] = '0fb58acf759c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_charts_id', table_name='charts')
    op.create_index(op.f('ix_charts_chartId'), 'charts', ['chartId'], unique=False)
    op.drop_index('ix_playlists_id', table_name='playlists')
    op.create_index(op.f('ix_playlists_playlistId'), 'playlists', ['playlistId'], unique=False)
    op.add_column('songs', sa.Column('reaction', sa.Integer(), nullable=True))
    op.drop_index('ix_songs_id', table_name='songs')
    op.create_index(op.f('ix_songs_songId'), 'songs', ['songId'], unique=False)
    op.drop_column('songs', 'release_date')
    op.drop_index('ix_users_id', table_name='users')
    op.create_index(op.f('ix_users_userId'), 'users', ['userId'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_userId'), table_name='users')
    op.create_index('ix_users_id', 'users', ['userId'], unique=False)
    op.add_column('songs', sa.Column('release_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_songs_songId'), table_name='songs')
    op.create_index('ix_songs_id', 'songs', ['songId'], unique=False)
    op.drop_column('songs', 'reaction')
    op.drop_index(op.f('ix_playlists_playlistId'), table_name='playlists')
    op.create_index('ix_playlists_id', 'playlists', ['playlistId'], unique=False)
    op.drop_index(op.f('ix_charts_chartId'), table_name='charts')
    op.create_index('ix_charts_id', 'charts', ['chartId'], unique=False)
    # ### end Alembic commands ###