"use client";

import {
  MessageCircle,
  Search,
  Lightbulb,
  Target,
  Footprints,
} from "lucide-react";

const steps = [
  {
    icon: MessageCircle,
    title: "1. 觉察与倾诉",
    desc: "自由地说出你的烦恼，不需要条理，语音或文字皆可。AI 会耐心倾听。",
    color: "bg-blue-100 text-blue-600",
  },
  {
    icon: Search,
    title: "2. 澄清事实",
    desc: "AI 帮你剥离情绪迷雾，区分「发生了什么」和「我感觉如何」，还原事实真相。",
    color: "bg-purple-100 text-purple-600",
  },
  {
    icon: Lightbulb,
    title: "3. 探索视角",
    desc: "跳出单一视角的局限。如果是旁观者会怎么看？还有什么没发现的可能性？",
    color: "bg-amber-100 text-amber-600",
  },
  {
    icon: Target,
    title: "4. 定义目标",
    desc: "从众多可能性中，找到你当下真正想要达成的结果。聚焦最重要的事。",
    color: "bg-orange-100 text-orange-600",
  },
  {
    icon: Footprints,
    title: "5. 承诺行动",
    desc: "将大目标拆解为微小、可执行的第一步。此时此刻，你能做什么？",
    color: "bg-emerald-100 text-emerald-600",
  },
];

export function ProcessSection() {
  return (
    <section id="process" className="bg-secondary/30 py-24">
      <div className="container mx-auto px-6">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            从混乱到清晰的 5 步旅程
          </h2>
          <p className="text-lg text-muted-foreground">
            基于认知行为疗法 (CBT) 与教练技术设计的结构化引导流程
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3 lg:grid-cols-5">
          {steps.map((step, i) => (
            <div key={i} className="group relative">
              <div className="flex flex-col items-center space-y-4 text-center">
                <div
                  className={`flex size-16 items-center justify-center rounded-2xl text-2xl shadow-sm transition-transform group-hover:scale-110 ${step.color}`}
                >
                  <step.icon className="size-8" />
                </div>
                <h3 className="text-lg font-semibold">{step.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {step.desc}
                </p>
              </div>
              {/* 连接线 (仅在桌面端显示) */}
              {i < steps.length - 1 && (
                <div className="absolute left-1/2 top-8 -z-10 hidden h-[2px] w-full translate-x-[50%] bg-gradient-to-r from-border to-transparent lg:block" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
