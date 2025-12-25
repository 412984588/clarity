"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";

import { useAuth } from "@/components/auth/AuthProvider";
import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

interface DeviceSession {
  id: string;
  name?: string;
  ip?: string;
  user_agent?: string;
  last_seen?: string;
  created_at?: string;
}

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const [devices, setDevices] = useState<DeviceSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get<DeviceSession[]>("/auth/devices");
        setDevices(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "加载设备失败");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);

  return (
    <div className="grid gap-6 md:grid-cols-[1.1fr_0.9fr]">
      <Card>
        <CardHeader>
          <CardTitle>个人信息</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <div>
            <p className="text-xs uppercase tracking-[0.2em]">姓名</p>
            <p className="text-base text-foreground">{user?.name || "-"}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em]">邮箱</p>
            <p className="text-base text-foreground">{user?.email || "-"}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em]">订阅</p>
            <p className="text-base text-foreground capitalize">
              {user?.subscription_tier || "free"}
            </p>
          </div>
          <Button variant="destructive" onClick={logout}>
            退出登录
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>设备管理</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {loading ? (
            <LoadingSpinner label="加载设备" />
          ) : error ? (
            <EmptyState title="设备加载失败" description={error} />
          ) : devices.length === 0 ? (
            <EmptyState title="暂无设备记录" />
          ) : (
            <div className="space-y-3">
              {devices.map((device) => (
                <div
                  key={device.id}
                  className="rounded-2xl border bg-muted/40 px-4 py-3 text-sm"
                >
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-foreground">
                      {device.name || device.user_agent || "未命名设备"}
                    </p>
                    <span className="text-xs text-muted-foreground">
                      {device.last_seen
                        ? format(new Date(device.last_seen), "MM/dd HH:mm")
                        : "-"}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {device.ip || "未知 IP"}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
