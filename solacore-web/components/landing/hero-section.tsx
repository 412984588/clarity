"use client";

import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";

export function HeroSection() {
  return (
    <section className="relative flex min-h-[90vh] flex-col items-center justify-center overflow-hidden pt-16">
      {/* 背景光效 */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/2 top-0 h-[600px] w-[1000px] -translate-x-1/2 rounded-[100%] bg-amber-100/40 opacity-70 mix-blend-multiply blur-3xl" />
        <div className="absolute bottom-0 right-0 h-[600px] w-[800px] rounded-[100%] bg-emerald-100/40 opacity-70 mix-blend-multiply blur-3xl" />
      </div>

      <div className="container flex flex-col items-center gap-8 px-6 text-center">
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
          <div className="inline-flex items-center rounded-full border bg-background/50 px-3 py-1 text-sm text-muted-foreground backdrop-blur-sm">
            <Sparkles className="mr-2 size-3.5 text-amber-500" />
            <span>Solacore 情绪梳理助手</span>
          </div>
        </div>

        <h1 className="animate-in fade-in slide-in-from-bottom-6 max-w-4xl text-5xl font-bold tracking-tight duration-700 ease-out delay-100 sm:text-7xl">
          把复杂的
          <span className="bg-gradient-to-r from-amber-500 to-orange-600 bg-clip-text text-transparent">
            情绪
          </span>
          <br />
          转化为清晰的
          <span className="bg-gradient-to-r from-emerald-500 to-teal-600 bg-clip-text text-transparent">
            行动
          </span>
        </h1>

        <p className="animate-in fade-in slide-in-from-bottom-6 max-w-2xl text-lg leading-relaxed text-muted-foreground duration-700 ease-out delay-200">
          很多时候，我们感到焦虑并不是因为事情多，而是因为看不清。
          <br className="hidden sm:block" />
          Solacore 引导你完成 5 步思考，从混乱中找回掌控感。
        </p>

        <div className="animate-in fade-in slide-in-from-bottom-6 flex flex-col items-center gap-4 duration-700 ease-out delay-300 sm:flex-row">
          <Button
            asChild
            size="lg"
            className="h-12 rounded-full px-8 text-base"
          >
            <Link href="/register">
              立即开始
              <ArrowRight className="ml-2 size-4" />
            </Link>
          </Button>
          <Button
            asChild
            variant="outline"
            size="lg"
            className="h-12 rounded-full bg-background/50 px-8 text-base backdrop-blur-sm"
          >
            <Link href="#process">了解原理</Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
