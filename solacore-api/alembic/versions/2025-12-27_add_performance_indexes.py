"""add performance indexes for subscriptions, active_sessions, devices

Revision ID: 7a8b9c0d1e2f
Revises: f1a2b3c4d5e6
Create Date: 2025-12-27 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a8b9c0d1e2f"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes using concurrent build."""
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_subscriptions_stripe_customer_id "
            "ON subscriptions (stripe_customer_id)"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_subscriptions_stripe_subscription_id "
            "ON subscriptions (stripe_subscription_id)"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_active_sessions_user_id_expires_at "
            "ON active_sessions (user_id, expires_at)"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_active_sessions_device_id "
            "ON active_sessions (device_id)"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY ix_devices_user_id_is_active "
            "ON devices (user_id, is_active)"
        )


def downgrade() -> None:
    """Remove performance indexes."""
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY ix_devices_user_id_is_active")
        op.execute("DROP INDEX CONCURRENTLY ix_active_sessions_device_id")
        op.execute("DROP INDEX CONCURRENTLY ix_active_sessions_user_id_expires_at")
        op.execute("DROP INDEX CONCURRENTLY ix_subscriptions_stripe_subscription_id")
        op.execute("DROP INDEX CONCURRENTLY ix_subscriptions_stripe_customer_id")
