"use client";

import { useEffect, useState } from "react";
import { Download } from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  getStatsOverview,
  exportStats,
  type StatsOverview,
} from "@/lib/stats-api";

interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
}

function StatCard({ title, value, subtitle }: StatCardProps) {
  return (
    <Card className="p-6">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
      {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
    </Card>
  );
}

export default function StatsPage() {
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const loadStats = async () => {
      try {
        setLoading(true);
        const data = await getStatsOverview();
        setStats(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "加载统计数据失败");
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, []);

  const handleExport = async (format: "json" | "csv") => {
    setExporting(true);
    try {
      const blob = await exportStats(format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `stats_report_${new Date().toISOString().split("T")[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "导出失败");
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-red-500">{error}</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const statusChartData = [
    { name: "进行中", value: stats.status_distribution.active },
    { name: "已完成", value: stats.status_distribution.completed },
    { name: "已放弃", value: stats.status_distribution.abandoned },
  ];

  const stepChartData = [
    { name: "接收", value: stats.step_distribution.receive },
    { name: "澄清", value: stats.step_distribution.clarify },
    { name: "重构", value: stats.step_distribution.reframe },
    { name: "选项", value: stats.step_distribution.options },
    { name: "承诺", value: stats.step_distribution.commit },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">数据统计</h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport("json")}
            disabled={exporting || !stats}
          >
            <Download className="mr-2 h-4 w-4" />
            {exporting ? "导出中..." : "导出 JSON"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport("csv")}
            disabled={exporting || !stats}
          >
            <Download className="mr-2 h-4 w-4" />
            {exporting ? "导出中..." : "导出 CSV"}
          </Button>
        </div>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="总会话数" value={stats.total_sessions} />
        <StatCard
          title="进行中"
          value={stats.status_distribution.active}
          subtitle="活跃会话"
        />
        <StatCard
          title="已完成"
          value={stats.status_distribution.completed}
          subtitle="完成会话"
        />
        <StatCard
          title="行动完成率"
          value={`${stats.action_completion.completion_rate}%`}
          subtitle={`${stats.action_completion.completed}/${stats.action_completion.total}`}
        />
      </div>

      <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <h2 className="mb-4 text-xl font-semibold">会话状态分布</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statusChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#3b82f6" name="数量" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 text-xl font-semibold">步骤分布</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stepChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#10b981" name="数量" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {stats.top_tags.length > 0 && (
        <Card className="mb-8 p-6">
          <h2 className="mb-4 text-xl font-semibold">热门标签</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.top_tags}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="tag" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#f59e0b" name="使用次数" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      {stats.daily_trend.length > 0 && (
        <Card className="p-6">
          <h2 className="mb-4 text-xl font-semibold">时间趋势（最近 30 天）</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.daily_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#8b5cf6"
                name="会话数"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
}
