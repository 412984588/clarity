"use client";

import Link from "next/link";

import { Button } from "@/components/ui/button";

export function SiteHeader() {
  return (
    <header className="fixed top-0 z-50 w-full border-b bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <div className="flex size-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-200 to-emerald-200">
            <span className="text-sm font-semibold text-foreground/80">S</span>
          </div>
          <span className="text-xl font-bold tracking-tight">Solacore</span>
        </div>

        <nav className="hidden items-center gap-8 text-sm font-medium text-muted-foreground md:flex">
          <Link
            href="#process"
            className="transition-colors hover:text-foreground"
          >
            核心流程
          </Link>
          <Link
            href="#features"
            className="transition-colors hover:text-foreground"
          >
            功能特性
          </Link>
        </nav>

        <div className="flex items-center gap-4">
          <Button asChild variant="ghost" size="sm">
            <Link href="/login">登录</Link>
          </Button>
          <Button asChild size="sm" className="rounded-full px-6">
            <Link href="/register">开始使用</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
