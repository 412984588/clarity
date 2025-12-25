import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  label?: string;
  className?: string;
}

export function LoadingSpinner({
  label = "加载中",
  className,
}: LoadingSpinnerProps) {
  return (
    <div
      className={cn("flex items-center gap-2 text-muted-foreground", className)}
    >
      <Loader2 className="size-4 animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  );
}
