import { CheckCircle2 } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface OptionCardProps {
  title: string;
  description: string;
  selected?: boolean;
  onToggle?: () => void;
  className?: string;
}

export function OptionCard({
  title,
  description,
  selected = false,
  onToggle,
  className,
}: OptionCardProps) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={cn("text-left", className)}
    >
      <Card
        className={cn(
          "group h-full border transition-all",
          selected
            ? "border-foreground bg-foreground/5 shadow-md"
            : "border-border hover:border-foreground/60"
        )}
      >
        <CardContent className="flex h-full flex-col gap-3">
          <div className="flex items-start justify-between gap-2">
            <div className="text-base font-semibold text-foreground">
              {title}
            </div>
            <CheckCircle2
              className={cn(
                "size-5 text-muted-foreground transition",
                selected && "text-foreground"
              )}
            />
          </div>
          <p className="text-sm text-muted-foreground">{description}</p>
        </CardContent>
      </Card>
    </button>
  );
}
