"""Prompt template API tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from app.models.prompt_template import PromptTemplate
from httpx import AsyncClient
from tests.conftest import TestingSessionLocal


async def _create_template(
    *,
    role_name: str,
    category: str,
    system_prompt: str,
    role_name_cn: str | None = None,
    welcome_message: str | None = None,
    icon_emoji: str | None = None,
    usage_count: int = 0,
    is_active: bool = True,
) -> PromptTemplate:
    template = PromptTemplate(
        id=uuid4(),
        role_name=role_name,
        role_name_cn=role_name_cn,
        category=category,
        system_prompt=system_prompt,
        welcome_message=welcome_message,
        icon_emoji=icon_emoji,
        usage_count=usage_count,
        is_active=is_active,
    )
    async with TestingSessionLocal() as session:
        session.add(template)
        await session.commit()
    return template


@pytest.mark.asyncio
async def test_list_templates_returns_active_templates(client: AsyncClient) -> None:
    active_template = await _create_template(
        role_name="English Teacher",
        category="learning",
        system_prompt="Teach English.",
        role_name_cn="英语老师",
        welcome_message="Hello!",
        icon_emoji="🎓",
    )
    await _create_template(
        role_name="Inactive Template",
        category="life",
        system_prompt="Hidden.",
        is_active=False,
    )

    response = await client.get("/api/v1/templates")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["templates"][0]["id"] == str(active_template.id)
    assert payload["templates"][0]["role_name"] == "English Teacher"


@pytest.mark.asyncio
async def test_list_templates_filters_by_category(client: AsyncClient) -> None:
    learning_template = await _create_template(
        role_name="English Teacher",
        category="learning",
        system_prompt="Teach English.",
    )
    await _create_template(
        role_name="Life Coach",
        category="life",
        system_prompt="Coach life.",
    )

    response = await client.get("/api/v1/templates", params={"category": "learning"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["templates"][0]["id"] == str(learning_template.id)


@pytest.mark.asyncio
async def test_list_templates_supports_pagination(client: AsyncClient) -> None:
    await _create_template(
        role_name="Template A",
        category="learning",
        system_prompt="Prompt A",
        usage_count=30,
    )
    template_b = await _create_template(
        role_name="Template B",
        category="learning",
        system_prompt="Prompt B",
        usage_count=20,
    )
    await _create_template(
        role_name="Template C",
        category="learning",
        system_prompt="Prompt C",
        usage_count=10,
    )

    response = await client.get(
        "/api/v1/templates",
        params={"limit": 1, "offset": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 3
    assert len(payload["templates"]) == 1
    assert payload["templates"][0]["id"] == str(template_b.id)


@pytest.mark.asyncio
async def test_get_template_returns_detail(client: AsyncClient) -> None:
    template = await _create_template(
        role_name="Career Counselor",
        category="work",
        system_prompt="Advise career.",
        welcome_message="Hi there!",
        icon_emoji="💼",
        usage_count=3,
    )

    response = await client.get(f"/api/v1/templates/{template.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(template.id)
    assert payload["system_prompt"] == "Advise career."
    assert payload["welcome_message"] == "Hi there!"
    assert payload["usage_count"] == 3


@pytest.mark.asyncio
async def test_get_template_not_found_returns_404(
    client: AsyncClient,
) -> None:
    response = await client.get(f"/api/v1/templates/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "TEMPLATE_NOT_FOUND"
