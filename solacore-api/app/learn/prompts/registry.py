"""工具元数据注册表"""

TOOL_REGISTRY = {
    "pareto": {
        "name": "80/20原则",
        "description": "抓住最关键的一小部分，先学最有用的内容。",
        "duration": "3-5分钟",
        "scenarios": ["入门梳理", "学习规划", "快速抓重点"],
    },
    "feynman": {
        "name": "费曼学习法",
        "description": "用最简单的话讲清楚，靠复述来确认理解。",
        "duration": "5-8分钟",
        "scenarios": ["概念理解", "自我检测", "复述讲解"],
    },
    "chunking": {
        "name": "分块学习法",
        "description": "把大主题切成小块，减少负担，逐步消化。",
        "duration": "5-10分钟",
        "scenarios": ["复杂主题", "系统学习", "降低信息量"],
    },
    "dual_coding": {
        "name": "双编码理论",
        "description": "文字配画面，让记忆有两个入口。",
        "duration": "5-8分钟",
        "scenarios": ["记忆强化", "流程理解", "抽象概念"],
    },
    "interleaving": {
        "name": "主题交叉法",
        "description": "把知识串起来，用对照和联想加深理解。",
        "duration": "5-10分钟",
        "scenarios": ["跨领域理解", "建立联系", "应用迁移"],
    },
    "retrieval": {
        "name": "检索练习",
        "description": "不看资料也能想起来，记忆会更牢。",
        "duration": "3-6分钟",
        "scenarios": ["复习巩固", "考前自测", "短时回忆"],
    },
    "spaced": {
        "name": "艾宾浩斯复习",
        "description": "用间隔复习对抗遗忘，学得更稳。",
        "duration": "2-4分钟",
        "scenarios": ["长期记忆", "学习计划", "复习提醒"],
    },
    "grow": {
        "name": "GROW模型",
        "description": "用目标、现状、选项、行动理清方向。",
        "duration": "6-10分钟",
        "scenarios": ["学习规划", "行动落地", "目标设定"],
    },
    "socratic": {
        "name": "苏格拉底提问",
        "description": "通过温和追问，引导自己找到答案。",
        "duration": "5-10分钟",
        "scenarios": ["思辨训练", "澄清概念", "深度理解"],
    },
    "error_driven": {
        "name": "错误驱动学习",
        "description": "先尝试再纠偏，从错误里找到正确路径。",
        "duration": "5-8分钟",
        "scenarios": ["技能练习", "应用题", "纠错提升"],
    },
}
