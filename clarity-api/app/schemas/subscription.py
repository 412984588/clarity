from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    price_id: str


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class PortalResponse(BaseModel):
    portal_url: str


class SubscriptionResponse(BaseModel):
    tier: str
    status: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False


class UsageResponse(BaseModel):
    tier: str
    sessions_used: int
    sessions_limit: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    is_lifetime: bool
