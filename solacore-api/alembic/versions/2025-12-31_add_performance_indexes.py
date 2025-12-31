"""add remaining performance indexes for sessions and auth

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-31 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add remaining performance indexes for sessions and auth.

    根据 OPTIMIZATION_REPORT.md 的性能分析：
    - solve_sessions: 会话列表查询加速 (5s → 0.1s, 50x)
    - learn_sessions: 学习会话列表加速 (5s → 0.1s, 50x)
    - devices: 设备查询优化 (1s → 0.02s, 50x)
    - users: OAuth 登录加速 (2s → 0.05s, 40x)
    """
    with op.get_context().autocommit_block():
        # 1. solve_sessions: 用户会话列表查询（分页）
        # 降序索引匹配 ORDER BY created_at DESC
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_solve_sessions_user_id_created_at "
            "ON solve_sessions (user_id, created_at DESC)"
        )

        # 2. learn_sessions: 学习会话列表查询（分页）
        # 降序索引匹配 ORDER BY created_at DESC
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_learn_sessions_user_id_created_at "
            "ON learn_sessions (user_id, created_at DESC)"
        )

        # 3. devices: 优化现有索引，添加 created_at 支持分页
        # 先删除旧索引
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_devices_user_id_is_active")
        # 创建部分索引（仅活跃设备），包含 created_at
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_devices_user_active_created "
            "ON devices (user_id, is_active, created_at) "
            "WHERE is_active = true"
        )

        # 4. users: OAuth 登录查询优化
        # 用于通过第三方认证信息查找用户
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_users_auth_provider "
            "ON users (auth_provider, auth_provider_id)"
        )


def downgrade() -> None:
    """Remove performance indexes."""
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_users_auth_provider")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_devices_user_active_created")
        op.execute(
            "DROP INDEX CONCURRENTLY IF EXISTS ix_learn_sessions_user_id_created_at"
        )
        op.execute(
            "DROP INDEX CONCURRENTLY IF EXISTS ix_solve_sessions_user_id_created_at"
        )

        # 恢复原索引
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_devices_user_id_is_active "
            "ON devices (user_id, is_active)"
        )
