import { Check } from "lucide-react";

import type { SolveStep } from "@/lib/types";
import { cn } from "@/lib/utils";

const steps: Array<{ key: SolveStep; label: string }> = [
  { key: "receive", label: "接收" },
  { key: "clarify", label: "澄清" },
  { key: "reframe", label: "重构" },
  { key: "options", label: "选项" },
  { key: "commit", label: "承诺" },
];

interface StepProgressProps {
  currentStep: SolveStep;
  className?: string;
}

export function StepProgress({ currentStep, className }: StepProgressProps) {
  const currentIndex = Math.max(
    0,
    steps.findIndex((step) => step.key === currentStep),
  );
  const progressPercent =
    steps.length > 1
      ? Math.round((currentIndex / (steps.length - 1)) * 100)
      : 0;
  const progressWidth =
    progressPercent === 0 ? "0%" : `calc(${progressPercent}% - 1rem)`;

  return (
    <div className={cn("rounded-2xl border bg-card/80 p-6", className)}>
      <div className="relative">
        <div className="absolute left-4 right-4 top-4 h-px bg-border" />
        <div
          className="absolute left-4 top-4 h-px bg-gradient-to-r from-foreground via-foreground to-transparent"
          style={{ width: progressWidth }}
        />
        <div className="grid grid-cols-5 gap-2">
          {steps.map((step, index) => {
            const isCurrent = index === currentIndex;
            const isCompleted = index < currentIndex;

            return (
              <div key={step.key} className="flex flex-col items-center gap-2">
                <div
                  className={cn(
                    "flex size-8 items-center justify-center rounded-full border text-xs font-semibold transition",
                    isCompleted &&
                      "border-foreground bg-foreground text-background",
                    isCurrent &&
                      "border-foreground bg-background text-foreground shadow-sm",
                  )}
                >
                  {isCompleted ? <Check className="size-4" /> : index + 1}
                </div>
                <span
                  className={cn(
                    "text-xs font-medium text-muted-foreground",
                    (isCompleted || isCurrent) && "text-foreground",
                  )}
                >
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
