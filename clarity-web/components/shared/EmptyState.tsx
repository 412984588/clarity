import { type ReactNode } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
  icon?: ReactNode;
  className?: string;
}

export function EmptyState({
  title,
  description,
  action,
  icon,
  className,
}: EmptyStateProps) {
  return (
    <Card className={cn("border-dashed", className)}>
      <CardHeader className="items-center text-center">
        {icon ? <div className="text-muted-foreground">{icon}</div> : null}
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-3 text-center">
        {description ? (
          <p className="text-sm text-muted-foreground">{description}</p>
        ) : null}
        {action ? <div>{action}</div> : null}
      </CardContent>
    </Card>
  );
}
