"""Datetime utilities for consistent UTC handling."""
from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC time as a naive datetime.

    This returns a naive datetime (no tzinfo) for compatibility with
    PostgreSQL TIMESTAMP WITHOUT TIME ZONE columns while avoiding
    the deprecated datetime.utcnow().
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
