from datetime import datetime
from typing import Optional

from app.schemas.fields import Field
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    price_id: str = Field(
        ...,
        description="Stripe 价格 ID",
        examples=["price_1234567890"],
    )


class CheckoutResponse(BaseModel):
    checkout_url: str = Field(
        ...,
        description="Stripe Checkout 跳转链接",
        examples=["https://checkout.stripe.com/c/pay/cs_test_123"],
    )
    session_id: str = Field(
        ...,
        description="Stripe Checkout Session ID",
        examples=["cs_test_1234567890"],
    )


class PortalResponse(BaseModel):
    portal_url: str = Field(
        ...,
        description="Stripe Customer Portal 跳转链接",
        examples=["https://billing.stripe.com/session/123"],
    )


class SubscriptionResponse(BaseModel):
    tier: str = Field(
        ...,
        description="订阅等级",
        examples=["standard"],
    )
    status: str = Field(
        ...,
        description="订阅状态",
        examples=["active"],
    )
    period_start: Optional[datetime] = Field(
        default=None,
        description="当前周期开始时间",
        examples=["2024-06-01T00:00:00Z"],
    )
    period_end: Optional[datetime] = Field(
        default=None,
        description="当前周期结束时间",
        examples=["2024-07-01T00:00:00Z"],
    )
    cancel_at_period_end: bool = Field(
        default=False,
        description="是否在周期结束时取消",
        examples=[False],
    )


class UsageResponse(BaseModel):
    tier: str = Field(
        ...,
        description="订阅等级",
        examples=["standard"],
    )
    sessions_used: int = Field(
        ...,
        description="当前周期已使用会话数",
        examples=[8],
    )
    sessions_limit: Optional[int] = Field(
        default=None,
        description="当前周期会话上限（None 表示无限制）",
        examples=[100],
    )
    period_start: Optional[datetime] = Field(
        default=None,
        description="当前周期开始时间",
        examples=["2024-06-01T00:00:00Z"],
    )
    period_end: Optional[datetime] = Field(
        default=None,
        description="当前周期结束时间",
        examples=["2024-07-01T00:00:00Z"],
    )
    is_lifetime: bool = Field(
        ...,
        description="是否为终身/无限制订阅",
        examples=[False],
    )
