"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { format } from "date-fns";

import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Session } from "@/lib/types";
import { listSessions } from "@/lib/session-api";

export default function SessionsPage() {
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

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <LoadingSpinner label="加载会话" />
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        title="加载会话失败"
        description={error}
        action={<Button onClick={() => window.location.reload()}>重试</Button>}
      />
    );
  }

  if (sessions.length === 0) {
    return (
      <EmptyState
        title="暂无会话记录"
        description="从 Solve 开始一次新的对话吧。"
        action={
          <Button asChild>
            <Link href="/solve">开始新对话</Link>
          </Button>
        }
      />
    );
  }

  return (
    <Card className="overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>创建时间</TableHead>
            <TableHead>当前步骤</TableHead>
            <TableHead>状态</TableHead>
            <TableHead className="text-right">查看</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sessions.map((session) => (
            <TableRow key={session.id}>
              <TableCell className="font-medium">
                {format(new Date(session.created_at), "yyyy/MM/dd HH:mm")}
              </TableCell>
              <TableCell>{session.current_step}</TableCell>
              <TableCell>{session.status}</TableCell>
              <TableCell className="text-right">
                <Button variant="ghost" asChild>
                  <Link href={`/sessions/${session.id}`}>查看</Link>
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
