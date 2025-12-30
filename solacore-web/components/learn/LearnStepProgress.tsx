"use client";

import { cn } from "@/lib/utils";
import type { LearnStep } from "@/lib/types";

const LEARN_STEPS: { key: LearnStep; label: string; method: string }[] = [
  { key: "start", label: "开始", method: "费曼学习法 + 80/20" },
  { key: "explore", label: "探索", method: "分块学习法 + 主题交叉" },
  { key: "practice", label: "练习", method: "双编码理论 + 费曼教学" },
  { key: "plan", label: "规划", method: "艾宾浩斯 + GROW模型" },
];

interface LearnStepProgressProps {
  currentStep: LearnStep;
  className?: string;
}

export function LearnStepProgress({
  currentStep,
  className,
}: LearnStepProgressProps) {
  const currentIndex = LEARN_STEPS.findIndex((s) => s.key === currentStep);

  return (
    <div className={cn("w-full", className)}>
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="font-medium text-foreground">学习进度</span>
        <span className="text-muted-foreground">
          {LEARN_STEPS[currentIndex]?.method}
        </span>
      </div>
      <div className="flex gap-2">
        {LEARN_STEPS.map((step, idx) => {
          const isActive = step.key === currentStep;
          const isCompleted = idx < currentIndex;

          return (
            <div key={step.key} className="flex flex-1 flex-col gap-1">
              <div
                className={cn(
                  "h-2 rounded-full transition-colors",
                  isCompleted
                    ? "bg-green-500"
                    : isActive
                      ? "bg-primary"
                      : "bg-muted"
                )}
              />
              <span
                className={cn(
                  "text-center text-xs",
                  isActive
                    ? "font-medium text-primary"
                    : isCompleted
                      ? "text-green-600"
                      : "text-muted-foreground"
                )}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
