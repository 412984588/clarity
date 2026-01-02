"""add prompt templates table

Revision ID: c4d5e6f7a8b9
Revises: b2c3d4e5f6a7
Create Date: 2026-01-02 10:00:00.000000

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from app.utils.datetime_utils import utc_now

# revision identifiers, used by Alembic.
revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create prompt templates table and seed data."""
    op.create_table(
        "prompt_templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("role_name", sa.String(length=100), nullable=False),
        sa.Column("role_name_cn", sa.String(length=100), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("welcome_message", sa.Text(), nullable=True),
        sa.Column("icon_emoji", sa.String(length=10), nullable=True),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_name"),
    )
    op.create_index(
        "ix_prompt_templates_category",
        "prompt_templates",
        ["category"],
        unique=False,
    )
    op.create_index(
        "ix_prompt_templates_usage_count",
        "prompt_templates",
        ["usage_count"],
        unique=False,
    )

    op.add_column("solve_sessions", sa.Column("template_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_solve_sessions_template_id",
        "solve_sessions",
        "prompt_templates",
        ["template_id"],
        ["id"],
    )

    prompt_templates = sa.table(
        "prompt_templates",
        sa.column("id", sa.UUID()),
        sa.column("role_name", sa.String()),
        sa.column("role_name_cn", sa.String()),
        sa.column("category", sa.String()),
        sa.column("system_prompt", sa.Text()),
        sa.column("welcome_message", sa.Text()),
        sa.column("icon_emoji", sa.String()),
        sa.column("usage_count", sa.Integer()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )
    now = utc_now()
    op.bulk_insert(
        prompt_templates,
        [
            {
                "id": uuid.uuid4(),
                "role_name": "English Teacher",
                "role_name_cn": "英语老师",
                "category": "learning",
                "system_prompt": "I want you to act as a spoken English teacher and improver. I will speak to you in English and you will reply to me in English to practice my spoken English. I want you to keep your reply neat, limiting the reply to 100 words. I want you to strictly correct my grammar mistakes, typos, and factual errors. I want you to ask me a question in your reply. Now let's start practicing, you could ask me a question first. Remember, I want you to strictly correct my grammar mistakes, typos, and factual errors.",
                "welcome_message": "Hello! I'm your English teacher. Let's practice! What would you like to talk about today?",
                "icon_emoji": "🎓",
                "usage_count": 0,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.uuid4(),
                "role_name": "Life Coach",
                "role_name_cn": "生活教练",
                "category": "life",
                "system_prompt": "I want you to act as a life coach. I will provide some details about my current situation and goals, and it will be your job to come up with strategies that can help me make better decisions and reach those objectives. This could involve offering advice on various topics, such as creating plans for achieving success or dealing with difficult emotions.",
                "welcome_message": "你好！我是你的生活教练。告诉我你现在的状况和目标，我会帮你制定行动计划。",
                "icon_emoji": "❤️",
                "usage_count": 0,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.uuid4(),
                "role_name": "Career Counselor",
                "role_name_cn": "职业顾问",
                "category": "work",
                "system_prompt": "I want you to act as a career counselor. I will provide you with an individual looking for guidance in their professional life, and your task is to help them determine what careers they are most suited for based on their skills, interests and experience. You should also conduct research into the various options available, explain the job market trends in different industries and advice on which qualifications would be beneficial for pursuing particular fields.",
                "welcome_message": "你好！我是职业顾问。告诉我你的技能、兴趣和经验，我会帮你找到最适合的职业方向。",
                "icon_emoji": "💼",
                "usage_count": 0,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.uuid4(),
                "role_name": "Friend",
                "role_name_cn": "倾听的朋友",
                "category": "life",
                "system_prompt": "I want you to act as my friend. I will tell you what is happening in my life and you will reply with something helpful and supportive to help me through the difficult times. Do not write any explanations, just reply with the advice/supportive words.",
                "welcome_message": "嗨，朋友！有什么烦心事吗？我在这里倾听。",
                "icon_emoji": "🤗",
                "usage_count": 0,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.uuid4(),
                "role_name": "Travel Guide",
                "role_name_cn": "旅行向导",
                "category": "entertainment",
                "system_prompt": "I want you to act as a travel guide. I will write you my location and you will suggest a place to visit near my location. In some cases, I will also give you the type of places I will visit. You will also suggest me places of similar type that are close to my first location.",
                "welcome_message": "你好！我是你的旅行向导。告诉我你在哪里，我会推荐附近的好去处。",
                "icon_emoji": "✈️",
                "usage_count": 0,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    """Drop prompt templates table and associations."""
    op.drop_constraint(
        "fk_solve_sessions_template_id", "solve_sessions", type_="foreignkey"
    )
    op.drop_column("solve_sessions", "template_id")
    op.drop_index("ix_prompt_templates_usage_count", table_name="prompt_templates")
    op.drop_index("ix_prompt_templates_category", table_name="prompt_templates")
    op.drop_table("prompt_templates")
