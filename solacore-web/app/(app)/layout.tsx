"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutGrid,
  MessageSquare,
  Layers,
  Settings as SettingsIcon,
} from "lucide-react";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/components/auth/AuthProvider";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutGrid },
  { href: "/solve", label: "Solve", icon: MessageSquare },
  { href: "/sessions", label: "Sessions", icon: Layers },
  { href: "/settings", label: "Settings", icon: SettingsIcon },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user } = useAuth();

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((part) => part[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "CL";

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[radial-gradient(circle_at_top,#f8fafc,transparent_55%),radial-gradient(circle_at_bottom,#fef3c7,transparent_35%)] text-foreground">
        <div className="mx-auto flex min-h-screen max-w-7xl gap-6 px-4 pb-24 pt-6 md:pb-6">
          <aside className="hidden w-60 flex-col rounded-3xl border bg-background/80 p-6 shadow-sm backdrop-blur md:flex">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-2xl bg-foreground text-base font-semibold text-background">
                C
              </div>
              <div>
                <p className="text-sm font-semibold">Clarity</p>
                <p className="text-xs text-muted-foreground">Focus workspace</p>
              </div>
            </div>

            <nav className="mt-10 flex flex-1 flex-col gap-2">
              {navItems.map((item) => {
                const isActive = pathname.startsWith(item.href);
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition",
                      isActive
                        ? "bg-foreground text-background shadow-sm"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground",
                    )}
                  >
                    <Icon className="size-4" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            <div className="mt-6 rounded-2xl border bg-muted/40 p-4 text-xs text-muted-foreground">
              每一步都被记录，随时回到你的思考轨迹。
            </div>
          </aside>

          <div className="flex flex-1 flex-col gap-6">
            <header className="flex flex-col gap-4 rounded-3xl border bg-background/80 px-6 py-4 shadow-sm backdrop-blur md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
                  Clarity Workspace
                </p>
                <h1 className="text-lg font-semibold">
                  {user?.name || "欢迎回来"}
                </h1>
              </div>
              <div className="flex items-center gap-3">
                <span className="rounded-full border px-3 py-1 text-xs text-muted-foreground">
                  {user?.subscription_tier || "free"}
                </span>
                <div className="flex size-10 items-center justify-center rounded-full bg-foreground text-sm font-semibold text-background">
                  {initials}
                </div>
              </div>
            </header>

            <main className="flex-1">{children}</main>
          </div>
        </div>

        <nav className="fixed bottom-4 left-1/2 z-10 flex w-[92%] -translate-x-1/2 items-center justify-between rounded-full border bg-background/90 px-6 py-3 shadow-lg backdrop-blur md:hidden">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex flex-col items-center gap-1 text-xs text-muted-foreground",
                  isActive && "text-foreground",
                )}
              >
                <Icon className="size-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </ProtectedRoute>
  );
}
