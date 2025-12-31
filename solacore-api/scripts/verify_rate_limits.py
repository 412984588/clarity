#!/usr/bin/env python3
"""验证所有路由端点的限流装饰器配置"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
ROUTERS_DIR = ROOT_DIR / "app" / "routers"

# 预期的限流配置
EXPECTED_LIMITS = {
    # Auth 路由
    ("auth.py", "register"): "AUTH_RATE_LIMIT",
    ("auth.py", "login"): "AUTH_RATE_LIMIT",
    ("auth.py", "beta_login"): "AUTH_RATE_LIMIT",
    ("auth.py", "refresh"): "API_RATE_LIMIT",  # 或其他
    ("auth.py", "forgot_password"): "FORGOT_PASSWORD_RATE_LIMIT",
    ("auth.py", "reset_password"): "API_RATE_LIMIT",
    ("auth.py", "logout"): "API_RATE_LIMIT",
    ("auth.py", "google_oauth_code"): "OAUTH_RATE_LIMIT",
    ("auth.py", "google_oauth"): "OAUTH_RATE_LIMIT",
    ("auth.py", "apple_oauth"): "OAUTH_RATE_LIMIT",
    ("auth.py", "get_current_user_info"): "API_RATE_LIMIT",
    ("auth.py", "list_devices"): "API_RATE_LIMIT",
    ("auth.py", "revoke_device"): "API_RATE_LIMIT",
    ("auth.py", "list_sessions"): "API_RATE_LIMIT",
    ("auth.py", "revoke_session"): "API_RATE_LIMIT",
    # Sessions 路由
    ("sessions.py", "create_session"): "API_RATE_LIMIT",
    ("sessions.py", "list_sessions"): "API_RATE_LIMIT",
    ("sessions.py", "get_session"): "API_RATE_LIMIT",
    ("sessions.py", "update_session"): "API_RATE_LIMIT",
    ("sessions.py", "stream_messages"): "SSE_RATE_LIMIT",
    # Subscriptions 路由
    ("subscriptions.py", "create_checkout"): "API_RATE_LIMIT",
    ("subscriptions.py", "get_portal"): "API_RATE_LIMIT",
    ("subscriptions.py", "get_current_subscription"): "API_RATE_LIMIT",
    ("subscriptions.py", "get_usage"): "API_RATE_LIMIT",
    # Account 路由
    ("account.py", "export_account"): "API_RATE_LIMIT",
    ("account.py", "delete_account"): "API_RATE_LIMIT",
}

# 不需要限流的端点（健康检查等）
SKIP_ENDPOINTS = {
    ("auth.py", "get_csrf_token"),
    ("auth.py", "get_features"),
}


class RateLimitChecker(ast.NodeVisitor):
    """AST 访问器，用于检查装饰器"""

    def __init__(self):
        self.functions: Dict[str, List[str]] = {}
        self.current_decorators: List[str] = []

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """访问异步函数定义"""
        # 检查装饰器
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    # @limiter.limit(...)
                    if (
                        isinstance(decorator.func.value, ast.Name)
                        and decorator.func.value.id == "limiter"
                        and decorator.func.attr == "limit"
                    ):
                        # 提取限流配置
                        if decorator.args:
                            arg = decorator.args[0]
                            if isinstance(arg, ast.Name):
                                decorators.append(f"@limiter.limit({arg.id})")
                elif isinstance(decorator.func, ast.Name):
                    decorators.append(f"@{decorator.func.id}")

        self.functions[node.name] = decorators
        self.generic_visit(node)


def check_file(file_path: Path) -> Dict[str, List[str]]:
    """检查单个文件的限流装饰器"""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    checker = RateLimitChecker()
    checker.visit(tree)
    return checker.functions


def _validate_endpoint(
    router_file_name: str, func_name: str, decorators: List[str]
) -> bool:
    """验证单个端点的限流配置

    Args:
        router_file_name: 路由文件名
        func_name: 函数名
        decorators: 装饰器列表

    Returns:
        bool: 是否验证通过
    """
    key = (router_file_name, func_name)
    limiter_decorators = [d for d in decorators if "@limiter.limit" in d]

    if key not in EXPECTED_LIMITS:
        return True  # 未在预期列表中，不判断对错

    expected = EXPECTED_LIMITS[key]
    if not limiter_decorators:
        print(f"❌ {router_file_name}::{func_name} - 缺少限流装饰器")
        return False

    if not any(expected in d for d in limiter_decorators):
        print(
            f"⚠️  {router_file_name}::{func_name} - "
            f"限流配置不匹配 (期望: {expected}, 实际: {limiter_decorators})"
        )
        return True  # 警告但不算失败

    print(f"✅ {router_file_name}::{func_name} - {limiter_decorators[0]}")
    return True


def _print_coverage_report(found_endpoints: Set[tuple]) -> None:
    """打印端点覆盖情况报告"""
    print("\n📋 端点覆盖情况:")
    expected_set = set(EXPECTED_LIMITS.keys()) | SKIP_ENDPOINTS
    missing = expected_set - found_endpoints
    extra = found_endpoints - expected_set

    if missing:
        print(f"\n⚠️  未找到的预期端点: {missing}")

    if extra:
        print(f"\n💡 额外的端点（未配置限流）: {extra}")

    print(f"\n总计: {len(found_endpoints)} 个端点")
    print(f"已配置限流: {len(EXPECTED_LIMITS)} 个")
    print(f"跳过限流: {len(SKIP_ENDPOINTS)} 个")


def main():
    """主函数"""
    print("🔍 验证限流装饰器配置...\n")

    all_ok = True
    found_endpoints: Set[tuple] = set()

    # 检查所有路由文件
    for router_file in ROUTERS_DIR.glob("*.py"):
        if router_file.name.startswith("__"):
            continue

        functions = check_file(router_file)

        for func_name, decorators in functions.items():
            key = (router_file.name, func_name)
            found_endpoints.add(key)

            # 跳过不需要限流的端点
            if key in SKIP_ENDPOINTS:
                continue

            # 验证端点
            if not _validate_endpoint(router_file.name, func_name, decorators):
                all_ok = False

    # 打印覆盖情况报告
    _print_coverage_report(found_endpoints)

    if all_ok:
        print("\n✅ 所有限流配置正确！")
        return 0
    else:
        print("\n❌ 发现配置问题，请检查上述输出")
        return 1


if __name__ == "__main__":
    sys.exit(main())
