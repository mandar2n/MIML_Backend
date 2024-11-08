"""Renamed columns

Revision ID: 0fb58acf759c
Revises: 
Create Date: 2024-11-08 14:30:49.310490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fb58acf759c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # User 테이블 칼럼명 변경
    op.alter_column('users', 'id', new_column_name='userId')
    op.alter_column('users', 'hashed_password', new_column_name='hashed_pw')
    op.alter_column('users', 'created_at', new_column_name='createdAt')

    # Song 테이블 칼럼명 변경
    op.alter_column('songs', 'id', new_column_name='songId')
    op.alter_column('songs', 'shared_by', new_column_name='sharedBy')
    op.alter_column('songs', 'shared_at', new_column_name='sharedAt')

    # Follow 테이블 칼럼명 변경
    op.alter_column('follows', 'followed_at', new_column_name='followedAt')

    # Playlist 테이블 칼럼명 변경
    op.alter_column('playlists', 'id', new_column_name='playlistId')
    op.alter_column('playlists', 'created_at', new_column_name='createdAt')

    # Chart 테이블 칼럼명 변경
    op.alter_column('charts', 'id', new_column_name='chartId')
    op.alter_column('charts', 'chart_type', new_column_name='chartType')
    op.alter_column('charts', 'generated_at', new_column_name='generatedAt')

def downgrade():
    # 칼럼명 되돌리기
    op.alter_column('users', 'userId', new_column_name='id')
    op.alter_column('users', 'hashed_pw', new_column_name='hashed_password')
    op.alter_column('users', 'createdAt', new_column_name='created_at')

    op.alter_column('songs', 'songId', new_column_name='id')
    op.alter_column('songs', 'sharedBy', new_column_name='shared_by')
    op.alter_column('songs', 'sharedAt', new_column_name='shared_at')

    op.alter_column('follows', 'followedAt', new_column_name='followed_at')

    op.alter_column('playlists', 'playlistId', new_column_name='id')
    op.alter_column('playlists', 'createdAt', new_column_name='created_at')

    op.alter_column('charts', 'chartId', new_column_name='id')
    op.alter_column('charts', 'chartType', new_column_name='chart_type')
    op.alter_column('charts', 'generatedAt', new_column_name='generated_at')