"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { format } from "date-fns";
import { Search, Trash2, X } from "lucide-react";

import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { TagBadge } from "@/components/session/TagBadge";
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
import {
  listSessions,
  deleteSession,
  type SessionSearchParams,
} from "@/lib/session-api";

function debounce(
  func: (params?: SessionSearchParams) => Promise<void>,
  wait: number,
): (params?: SessionSearchParams) => void {
  let timeout: NodeJS.Timeout;
  return (params?: SessionSearchParams) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(params), wait);
  };
}

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<Session | null>(null);
  const [deleting, setDeleting] = useState(false);

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedStatus, setSelectedStatus] = useState<string>("");

  const loadSessions = useCallback(async (params?: SessionSearchParams) => {
    try {
      setLoading(true);
      const data = await listSessions(params);
      setSessions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载会话失败");
    } finally {
      setLoading(false);
    }
  }, []);

  const debouncedSearch = useMemo(
    () => debounce(loadSessions, 300),
    [loadSessions],
  );

  useEffect(() => {
    const params: SessionSearchParams = {};
    if (searchQuery) params.q = searchQuery;
    if (selectedTags.length > 0) params.tags = selectedTags.join(",");
    if (selectedStatus) params.status = selectedStatus;

    debouncedSearch(params);
  }, [searchQuery, selectedTags, selectedStatus, debouncedSearch]);

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

  const allTags = useMemo(() => {
    const tagSet = new Set<string>();
    sessions.forEach((session) => {
      session.tags?.forEach((tag) => tagSet.add(tag));
    });
    return Array.from(tagSet).sort();
  }, [sessions]);

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

  if (
    sessions.length === 0 &&
    !searchQuery &&
    selectedTags.length === 0 &&
    !selectedStatus
  ) {
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
      <div className="mb-4 space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索会话..."
            className="w-full pl-10 pr-10 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <X className="w-4 h-4 text-gray-400 hover:text-gray-600" />
            </button>
          )}
        </div>

        <div className="flex gap-2 flex-wrap">
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-1.5 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">所有状态</option>
            <option value="active">进行中</option>
            <option value="completed">已完成</option>
            <option value="archived">已归档</option>
          </select>

          {allTags.length > 0 && (
            <select
              value=""
              onChange={(e) => {
                const tag = e.target.value;
                if (tag && !selectedTags.includes(tag)) {
                  setSelectedTags([...selectedTags, tag]);
                }
              }}
              className="px-3 py-1.5 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">添加标签过滤...</option>
              {allTags.map((tag) => (
                <option
                  key={tag}
                  value={tag}
                  disabled={selectedTags.includes(tag)}
                >
                  {tag}
                </option>
              ))}
            </select>
          )}

          {selectedTags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
            >
              {tag}
              <button
                onClick={() =>
                  setSelectedTags(selectedTags.filter((t) => t !== tag))
                }
                className="hover:bg-blue-200 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      </div>

      <Card className="overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>内容</TableHead>
              <TableHead>标签</TableHead>
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
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {session.tags && session.tags.length > 0 ? (
                      session.tags.map((tag) => (
                        <TagBadge key={tag} tag={tag} variant="outline" />
                      ))
                    ) : (
                      <span className="text-xs text-gray-400">无标签</span>
                    )}
                  </div>
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
