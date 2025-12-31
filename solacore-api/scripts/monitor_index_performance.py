#!/usr/bin/env python3
"""
数据库索引性能监控脚本

功能：
1. 连接到 PostgreSQL 数据库
2. 查询 pg_stat_user_indexes 视图
3. 显示每个索引的统计信息（扫描次数、读取行数、获取行数）
4. 计算索引效率（idx_scan / table_scan 比率）
5. 识别未使用的索引（idx_scan = 0）
6. 识别低效索引（读取多但扫描少）

使用方法：
    python scripts/monitor_index_performance.py

环境变量：
    DATABASE_URL - PostgreSQL 连接字符串
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def format_number(num: int | None) -> str:
    """格式化数字，添加千位分隔符"""
    if num is None:
        return "N/A"
    if num == 0:
        return "0"
    return f"{num:,}"


def calculate_efficiency(idx_scan: int, idx_tup_read: int) -> str:
    """计算索引效率（每次扫描读取的平均行数）"""
    if idx_scan == 0:
        return "N/A"
    avg_rows_per_scan = idx_tup_read / idx_scan
    if avg_rows_per_scan < 10:
        return f"{avg_rows_per_scan:.2f} (高效)"
    elif avg_rows_per_scan < 100:
        return f"{avg_rows_per_scan:.2f} (中等)"
    else:
        return f"{avg_rows_per_scan:.2f} (低效)"


def calculate_usage_ratio(idx_scan: int, seq_scan: int) -> str:
    """计算索引使用率（idx_scan / (idx_scan + seq_scan)）"""
    total_scans = idx_scan + seq_scan
    if total_scans == 0:
        return "N/A"
    ratio = (idx_scan / total_scans) * 100
    if ratio > 80:
        return f"{ratio:.1f}% (优秀)"
    elif ratio > 50:
        return f"{ratio:.1f}% (良好)"
    elif ratio > 20:
        return f"{ratio:.1f}% (一般)"
    else:
        return f"{ratio:.1f}% (差)"


async def get_index_stats(database_url: str) -> list[dict[str, Any]]:
    """查询索引统计信息"""
    engine = create_async_engine(database_url, echo=False)

    query = text("""
        SELECT
            psi.schemaname AS schema_name,
            psi.relname AS table_name,
            psi.indexrelname AS index_name,
            psi.idx_scan,
            psi.idx_tup_read,
            psi.idx_tup_fetch,
            pg_size_pretty(pg_relation_size(psi.indexrelid)) AS index_size,
            pg_relation_size(psi.indexrelid) AS index_size_bytes,
            -- 表的统计信息
            COALESCE(pst.seq_scan, 0) AS seq_scan,
            COALESCE(pst.n_live_tup, 0) AS table_rows
        FROM pg_stat_user_indexes psi
        LEFT JOIN pg_stat_user_tables pst
            ON psi.schemaname = pst.schemaname
            AND psi.relname = pst.relname
        WHERE psi.schemaname = 'public'
        ORDER BY psi.idx_scan DESC, psi.idx_tup_read DESC
    """)

    try:
        async with engine.connect() as conn:
            result = await conn.execute(query)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
    finally:
        await engine.dispose()


def print_summary(stats: list[dict[str, Any]]) -> None:
    """打印汇总信息"""
    total_indexes = len(stats)
    unused_indexes = [s for s in stats if s["idx_scan"] == 0]
    low_usage_indexes = [s for s in stats if s["idx_scan"] > 0 and s["idx_scan"] < 10]
    total_size_bytes = sum(s["index_size_bytes"] for s in stats)

    print("\n" + "=" * 100)
    print(f"📊 索引性能监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print(f"\n总索引数: {total_indexes}")
    print(
        f"未使用索引: {len(unused_indexes)} ({len(unused_indexes) / total_indexes * 100:.1f}%)"
    )
    print(f"低使用索引: {len(low_usage_indexes)} (扫描次数 < 10)")
    print(f"总索引大小: {format_size(total_size_bytes)}")
    print()


def format_size(size_bytes: int) -> str:
    """格式化字节大小"""
    size_float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_float < 1024:
            return f"{size_float:.2f} {unit}"
        size_float /= 1024
    return f"{size_float:.2f} TB"


def print_index_table(stats: list[dict[str, Any]]) -> None:
    """打印索引统计表格"""
    print("=" * 150)
    print(
        f"{'表名':<20} {'索引名':<30} {'扫描次数':<12} {'读取行数':<12} {'获取行数':<12} {'索引大小':<10} {'索引效率':<20} {'使用率':<15}"
    )
    print("=" * 150)

    for stat in stats:
        table_name = stat["table_name"]
        index_name = stat["index_name"]
        idx_scan = stat["idx_scan"] or 0
        idx_tup_read = stat["idx_tup_read"] or 0
        idx_tup_fetch = stat["idx_tup_fetch"] or 0
        index_size = stat["index_size"]
        seq_scan = stat["seq_scan"] or 0

        efficiency = calculate_efficiency(idx_scan, idx_tup_read)
        usage_ratio = calculate_usage_ratio(idx_scan, seq_scan)

        # 高亮未使用的索引
        prefix = "❌ " if idx_scan == 0 else "  "

        print(
            f"{prefix}{table_name:<20} {index_name:<30} {format_number(idx_scan):<12} {format_number(idx_tup_read):<12} {format_number(idx_tup_fetch):<12} {index_size:<10} {efficiency:<20} {usage_ratio:<15}"
        )


def print_recommendations(stats: list[dict[str, Any]]) -> None:
    """打印优化建议"""
    print("\n" + "=" * 100)
    print("💡 优化建议")
    print("=" * 100)

    unused_indexes = [s for s in stats if s["idx_scan"] == 0]
    if unused_indexes:
        print("\n⚠️ 未使用的索引（考虑删除以节省空间）：")
        for stat in unused_indexes[:10]:  # 最多显示 10 个
            print(
                f"  - {stat['table_name']}.{stat['index_name']} ({stat['index_size']})"
            )

    low_efficiency = [
        s
        for s in stats
        if s["idx_scan"] > 0
        and s["idx_tup_read"] > 0
        and (s["idx_tup_read"] / s["idx_scan"]) > 100
    ]
    if low_efficiency:
        print("\n⚠️ 低效索引（每次扫描读取大量行，可能需要优化）：")
        for stat in low_efficiency[:10]:  # 最多显示 10 个
            avg_rows = stat["idx_tup_read"] / stat["idx_scan"]
            print(
                f"  - {stat['table_name']}.{stat['index_name']} (平均每次扫描 {avg_rows:.0f} 行)"
            )

    low_usage = [
        s
        for s in stats
        if s["idx_scan"] > 0
        and s["seq_scan"] is not None
        and s["seq_scan"] > 0
        and (s["idx_scan"] / (s["idx_scan"] + s["seq_scan"])) < 0.2
    ]
    if low_usage:
        print("\n⚠️ 使用率低的索引（表扫描次数远多于索引扫描）：")
        for stat in low_usage[:10]:  # 最多显示 10 个
            idx_scan = stat["idx_scan"]
            seq_scan = stat["seq_scan"]
            ratio = (idx_scan / (idx_scan + seq_scan)) * 100
            print(
                f"  - {stat['table_name']}.{stat['index_name']} (使用率 {ratio:.1f}%, 索引扫描 {idx_scan}, 表扫描 {seq_scan})"
            )

    if not unused_indexes and not low_efficiency and not low_usage:
        print("\n✅ 所有索引使用情况良好，无需优化")


async def main() -> None:
    """主函数"""
    # 获取数据库连接字符串
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ 错误: 未设置 DATABASE_URL 环境变量")
        print("\n使用方法：")
        print("  export DATABASE_URL='postgresql+asyncpg://user:pass@host:port/dbname'")
        print("  python scripts/monitor_index_performance.py")
        sys.exit(1)

    print("🔍 正在查询数据库索引统计信息...\n")

    try:
        stats = await get_index_stats(database_url)

        if not stats:
            print("⚠️ 未找到任何索引")
            return

        print_summary(stats)
        print_index_table(stats)
        print_recommendations(stats)

        print("\n" + "=" * 100)
        print("📝 注意事项:")
        print("  - 统计数据是累积的，自上次统计重置以来的总和")
        print("  - 可以使用 pg_stat_reset() 重置统计数据")
        print("  - 删除索引前请先在测试环境验证影响")
        print("=" * 100)

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
