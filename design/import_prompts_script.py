#!/usr/bin/env python3
"""
从 awesome-chatgpt-prompts 导入提示词模板

使用方法:
1. 下载 CSV: curl -O https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv
2. 运行脚本: python import_prompts_script.py prompts.csv
"""

import csv

# 角色分类映射（根据角色名称自动分类）
CATEGORY_MAPPING = {
    "learning": [
        "English Teacher",
        "Teacher",
        "Instructor",
        "Tutor",
        "Academic",
        "Etymologist",
        "Historian",
        "Philosopher",
        "Mathematician",
        "Essay Writer",
        "Poet",
        "Novelist",
        "Screenwriter",
        "Journalist",
        "Note-taking Assistant",
        "Language Detector",
        "Plagiarism Checker",
    ],
    "life": [
        "Life Coach",
        "Motivational Coach",
        "Relationship Coach",
        "Mental Health Adviser",
        "Psychologist",
        "Friend",
        "Counselor",
        "Self-Help Book",
        "Yogi",
        "Personal Trainer",
        "Dietitian",
        "Doctor",
        "Dentist",
        "Hypnotherapist",
        "Astrologer",
        "Dream Interpreter",
    ],
    "work": [
        "Career Counselor",
        "Interviewer",
        "Resume",
        "Recruiter",
        "Salesperson",
        "Advertiser",
        "Social Media Manager",
        "CEO",
        "Product Manager",
        "Tech Reviewer",
        "Developer Relations",
        "IT Architect",
        "Financial Analyst",
        "Accountant",
        "Investment Manager",
        "Real Estate Agent",
        "Logistician",
        "Startup Tech Lawyer",
    ],
    "entertainment": [
        "Travel Guide",
        "Chef",
        "Personal Chef",
        "Sommelier",
        "Interior Decorator",
        "Storyteller",
        "Stand-up Comedian",
        "Magician",
        "Makeup Artist",
        "Babysitter",
        "Pet Behaviorist",
        "Personal Stylist",
        "Florist",
        "Composer",
        "Rapper",
        "Classical Music Composer",
        "Song Recommender",
        "Movie Critic",
        "Football Commentator",
        "Chess Player",
        "Tic-Tac-Toe Game",
    ],
    "tech": [
        "Linux Terminal",
        "JavaScript Console",
        "SQL Terminal",
        "Excel Sheet",
        "Python Interpreter",
        "R Programming Interpreter",
        "PHP Interpreter",
        "IT Expert",
        "Cyber Security Specialist",
        "Web Design Consultant",
        "Senior Frontend Developer",
        "UX/UI Developer",
        "Regex Generator",
        "Commit Message Generator",
        "Diagram Generator",
        "Web Browser",
        "SVG Designer",
        "ASCII Artist",
        "Solr Search Engine",
        "Stackoverflow Post",
    ],
}

# 中文名称映射（常用角色）
CHINESE_NAME_MAPPING = {
    "English Teacher": "英语老师",
    "Life Coach": "生活教练",
    "Career Counselor": "职业顾问",
    "Friend": "倾听的朋友",
    "Travel Guide": "旅行向导",
    "Chef": "私人厨师",
    "Personal Trainer": "健身教练",
    "Mental Health Adviser": "心理健康顾问",
    "Motivational Coach": "励志教练",
    "Relationship Coach": "情感顾问",
    "Resume": "简历助手",
    "Interviewer": "面试官",
    "Storyteller": "故事大师",
    "Poet": "诗人",
    "Stand-up Comedian": "脱口秀演员",
    "Interior Decorator": "室内设计师",
    "Personal Stylist": "造型顾问",
    "Dietitian": "营养师",
    "Salesperson": "销售顾问",
    "Social Media Manager": "社交媒体经理",
}

# Emoji 映射
EMOJI_MAPPING = {
    "learning": "📚",
    "life": "❤️",
    "work": "💼",
    "entertainment": "🎨",
    "tech": "💻",
}


def categorize_role(role_name: str) -> str:
    """根据角色名称判断分类"""
    for category, keywords in CATEGORY_MAPPING.items():
        if any(keyword in role_name for keyword in keywords):
            return category
    return "entertainment"  # 默认分类


def generate_welcome_message(role_name: str, category: str) -> str:
    """生成欢迎消息"""
    messages = {
        "learning": f"Hello! I'm your {role_name}. Let's learn together!",
        "life": f"你好！我是你的{CHINESE_NAME_MAPPING.get(role_name, role_name)}。有什么可以帮你的吗？",
        "work": f"你好！我是{CHINESE_NAME_MAPPING.get(role_name, role_name)}。准备好开始了吗？",
        "entertainment": f"嗨！我是{CHINESE_NAME_MAPPING.get(role_name, role_name)}。我们开始吧！",
        "tech": f"$ {role_name} initialized. Ready to assist.",
    }
    return messages.get(category, f"Hello! I'm your {role_name}.")


def parse_csv_and_generate_sql(csv_file: str, output_file: str = "prompts_seed.sql"):
    """解析 CSV 并生成 SQL 插入语句"""

    sql_statements = []
    sql_statements.append("-- 导入提示词模板数据")
    sql_statements.append("-- 来源: https://github.com/f/awesome-chatgpt-prompts\n")

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            role_name = row["act"].strip()
            prompt = row["prompt"].strip().replace("'", "''")  # SQL 转义

            # 分类
            category = categorize_role(role_name)

            # 中文名
            role_name_cn = CHINESE_NAME_MAPPING.get(role_name, "")

            # Emoji
            icon_emoji = EMOJI_MAPPING.get(category, "🤖")

            # 欢迎消息
            welcome_message = generate_welcome_message(role_name, category)

            # 描述（截取提示词前 100 字符）
            description = prompt[:100] + "..." if len(prompt) > 100 else prompt

            # 生成 SQL
            sql = f"""
INSERT INTO prompt_templates (role_name, role_name_cn, category, system_prompt, welcome_message, icon_emoji, description, is_active)
VALUES (
    '{role_name}',
    {f"'{role_name_cn}'" if role_name_cn else "NULL"},
    '{category}',
    '{prompt}',
    '{welcome_message}',
    '{icon_emoji}',
    '{description}',
    true
) ON CONFLICT (role_name) DO NOTHING;
"""
            sql_statements.append(sql.strip())

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))

    print(f"✅ 已生成 {output_file}")
    print(f"📊 共 {len(sql_statements) - 2} 个提示词模板")


def generate_priority_list():
    """生成推荐的 20 个优先角色"""
    priority_roles = [
        # 学习成长（5个）
        "English Teacher",
        "Career Counselor",
        "Essay Writer",
        "Note-taking Assistant",
        "Etymologist",
        # 生活健康（5个）
        "Life Coach",
        "Mental Health Adviser",
        "Friend",
        "Personal Trainer",
        "Dietitian",
        # 工作职场（5个）
        "Resume",
        "Interviewer",
        "Social Media Manager",
        "Salesperson",
        "IT Architect",
        # 娱乐创意（5个）
        "Storyteller",
        "Travel Guide",
        "Chef",
        "Interior Decorator",
        "Poet",
    ]

    print("\n📌 推荐优先集成的 20 个角色：")
    for i, role in enumerate(priority_roles, 1):
        category = categorize_role(role)
        emoji = EMOJI_MAPPING.get(category, "🤖")
        cn_name = CHINESE_NAME_MAPPING.get(role, "")
        print(f"{i:2d}. {emoji} {role:<25} ({cn_name})")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python import_prompts_script.py prompts.csv")
        print("\n首先下载 CSV:")
        print(
            "  curl -O https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv"
        )
        sys.exit(1)

    csv_file = sys.argv[1]
    parse_csv_and_generate_sql(csv_file)
    generate_priority_list()
