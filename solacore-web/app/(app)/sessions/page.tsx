"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { format } from "date-fns";
import { Trash2 } from "lucide-react";

import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Session } from "@/lib/types";
import { listSessions, deleteSession } from "@/lib/session-api";

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<Session | null>(null);
  const [deleting, setDeleting] = useState(false);

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

  const handleDeleteClick = (session: Session) => {
    setSessionToDelete(session);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!sessionToDelete) return;

    setDeleting(true);
    try {
      await deleteSession(sessionToDelete.id);
      // 从列表中移除已删除的会话
      setSessions((prev) => prev.filter((s) => s.id !== sessionToDelete.id));
      setDeleteDialogOpen(false);
      setSessionToDelete(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "删除会话失败");
    } finally {
      setDeleting(false);
    }
  };

  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
    setSessionToDelete(null);
  };

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
    <>
      <Card className="overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>内容</TableHead>
              <TableHead>创建时间</TableHead>
              <TableHead>当前步骤</TableHead>
              <TableHead>状态</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sessions.map((session) => (
              <TableRow key={session.id}>
                <TableCell className="max-w-md truncate font-medium">
                  {session.first_message || "新会话"}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {format(new Date(session.created_at), "yyyy/MM/dd HH:mm")}
                </TableCell>
                <TableCell>{session.current_step}</TableCell>
                <TableCell>{session.status}</TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    <Button variant="ghost" asChild>
                      <Link href={`/sessions/${session.id}`}>查看</Link>
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteClick(session)}
                      aria-label="删除会话"
                    >
                      <Trash2 className="size-4 text-muted-foreground hover:text-destructive" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* 删除确认对话框 */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除会话</DialogTitle>
            <DialogDescription>
              您确定要删除这个会话吗？此操作无法撤销，会话的所有消息和历史记录都将被永久删除。
            </DialogDescription>
          </DialogHeader>
          {sessionToDelete && (
            <div className="rounded-lg border bg-muted/50 p-3">
              <p className="text-sm font-medium">
                {sessionToDelete.first_message || "新会话"}
              </p>
              <p className="text-xs text-muted-foreground">
                {format(
                  new Date(sessionToDelete.created_at),
                  "yyyy/MM/dd HH:mm",
                )}
              </p>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleCancelDelete}
              disabled={deleting}
            >
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleting}
            >
              {deleting ? "删除中..." : "确认删除"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
