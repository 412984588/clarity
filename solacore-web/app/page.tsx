"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,#fef3c7,transparent_45%),radial-gradient(circle_at_bottom,#c7f9e8,transparent_45%)]">
      <div className="absolute -left-24 -top-24 size-72 rounded-full bg-amber-200/50 blur-3xl" />
      <div className="absolute -bottom-32 right-0 size-96 rounded-full bg-emerald-200/60 blur-3xl" />

      <div className="relative mx-auto flex min-h-screen max-w-5xl items-center justify-center px-6 py-16">
        <div className="flex flex-col items-center gap-8 text-center">
          <div className="inline-flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.3em] text-foreground/70">
            <span className="h-px w-12 bg-foreground/40" />
            Solacore Web
            <span className="h-px w-12 bg-foreground/40" />
          </div>

          <h1 className="max-w-3xl text-5xl font-semibold leading-tight text-foreground md:text-6xl">
            把你复杂的情绪
            <span className="block text-foreground">转化成清晰行动</span>
          </h1>

          <p className="max-w-2xl text-lg leading-relaxed text-muted-foreground">
            从澄清到承诺，Solacore 带你完成五步思考流程，
            <br />
            留下可执行的下一步。
          </p>

          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="rounded-full border px-4 py-2">私密对话</div>
            <div className="rounded-full border px-4 py-2">结构化引导</div>
            <div className="rounded-full border px-4 py-2">立即可用</div>
          </div>

          <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row">
            <Button asChild size="lg" className="gap-2">
              <Link href="/login">
                开始使用
                <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/login">登录</Link>
            </Button>
          </div>

          <div className="mt-16 rounded-3xl border bg-background/80 p-8 shadow-xl backdrop-blur">
            <div className="grid gap-6 md:grid-cols-3">
              <div className="space-y-2">
                <div className="flex size-12 items-center justify-center rounded-2xl bg-amber-100 text-xl">
                  1
                </div>
                <h3 className="font-semibold">澄清</h3>
                <p className="text-sm text-muted-foreground">
                  说出你的困扰，不用担心条理
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex size-12 items-center justify-center rounded-2xl bg-emerald-100 text-xl">
                  2
                </div>
                <h3 className="font-semibold">探索</h3>
                <p className="text-sm text-muted-foreground">
                  AI 引导你看清问题本质
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex size-12 items-center justify-center rounded-2xl bg-blue-100 text-xl">
                  3
                </div>
                <h3 className="font-semibold">行动</h3>
                <p className="text-sm text-muted-foreground">
                  得到清晰可执行的下一步
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
