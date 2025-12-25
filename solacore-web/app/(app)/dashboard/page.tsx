"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { format } from "date-fns";
import { ArrowUpRight } from "lucide-react";

import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/components/auth/AuthProvider";
import type { Session } from "@/lib/types";
import { listSessions } from "@/lib/session-api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await listSessions();
        setSessions(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "加载会话失败");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);

  const recentSessions = useMemo(() => sessions.slice(0, 5), [sessions]);

  return (
    <div className="grid gap-6">
      <section className="grid gap-4 md:grid-cols-[1.5fr_1fr]">
        <Card className="bg-gradient-to-br from-background to-muted/70">
          <CardHeader>
            <CardTitle className="text-2xl">
              {user?.name ? `欢迎回来，${user.name}` : "欢迎回来"}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              今天想从哪个问题开始？继续梳理、澄清或重新框定你的思路。
            </p>
            <Button asChild>
              <Link href="/solve">开始新对话</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">订阅状态</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-2xl border bg-muted/40 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                当前方案
              </p>
              <p className="text-lg font-semibold capitalize">
                {user?.subscription_tier || "free"}
              </p>
            </div>
            <Button variant="outline" asChild>
              <Link href="/paywall">
                查看升级方案
                <ArrowUpRight className="size-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">最近会话</h2>
          <Button variant="ghost" asChild>
            <Link href="/sessions">查看全部</Link>
          </Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner label="加载会话" />
          </div>
        ) : error ? (
          <EmptyState
            title="会话加载失败"
            description={error}
            action={
              <Button onClick={() => window.location.reload()}>刷新</Button>
            }
          />
        ) : recentSessions.length === 0 ? (
          <EmptyState
            title="还没有会话"
            description="开始你的第一个清晰对话，记录下一步行动。"
            action={
              <Button asChild>
                <Link href="/solve">立即开始</Link>
              </Button>
            }
          />
        ) : (
          <div className="grid gap-3">
            {recentSessions.map((session) => (
              <Link
                key={session.id}
                href={`/sessions/${session.id}`}
                className="rounded-2xl border bg-background/80 px-4 py-4 transition hover:border-foreground/50"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold">会话 {session.id}</p>
                    <p className="text-xs text-muted-foreground">
                      {format(new Date(session.created_at), "yyyy/MM/dd HH:mm")}
                    </p>
                  </div>
                  <span className="rounded-full border px-3 py-1 text-xs text-muted-foreground">
                    {session.current_step}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
