"""add more performance indexes for auth and subscriptions

Revision ID: c1d2e3f4g5h6
Revises: b2c3d4e5f6a7
Create Date: 2026-01-01 04:27:06.276294

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1d2e3f4g5h6"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add more performance indexes for auth and subscriptions.

    根据 OPTIMIZATION_REPORT.md 的性能分析：
    - active_sessions: 验证会话有效性 (user_id, expires_at)
    - subscriptions: Webhook 查询加速 (stripe_customer_id, stripe_subscription_id)
    - password_reset_tokens: 密码重置验证 (token_hash)
    """
    with op.get_context().autocommit_block():
        # 1. active_sessions: 验证会话有效性
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_active_sessions_user_expires "
            "ON active_sessions (user_id, expires_at)"
        )

        # 2. subscriptions: Webhook 查询优化 (Customer ID)
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_subscriptions_stripe_customer_id "
            "ON subscriptions (stripe_customer_id)"
        )

        # 3. subscriptions: Webhook 查询优化 (Subscription ID)
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_subscriptions_stripe_subscription_id "
            "ON subscriptions (stripe_subscription_id)"
        )

        # 4. password_reset_tokens: 密码重置验证
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_password_reset_token_hash "
            "ON password_reset_tokens (token_hash)"
        )


def downgrade() -> None:
    """Remove performance indexes."""
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_password_reset_token_hash")
        op.execute(
            "DROP INDEX CONCURRENTLY IF EXISTS ix_subscriptions_stripe_subscription_id"
        )
        op.execute(
            "DROP INDEX CONCURRENTLY IF EXISTS ix_subscriptions_stripe_customer_id"
        )
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_active_sessions_user_expires")
