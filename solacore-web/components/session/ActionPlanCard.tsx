"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CheckCircle2, Circle } from "lucide-react";
import { toast } from "sonner";

interface ActionPlanCardProps {
  sessionId: string;
  action: string;
  completed: boolean;
  onToggle: (completed: boolean) => Promise<void>;
}

export function ActionPlanCard({
  sessionId,
  action,
  completed,
  onToggle,
}: ActionPlanCardProps) {
  const [isCompleted, setIsCompleted] = useState(completed);
  const [isLoading, setIsLoading] = useState(false);

  const handleToggle = async () => {
    setIsLoading(true);
    try {
      const newState = !isCompleted;
      await onToggle(newState);
      setIsCompleted(newState);
      toast.success(newState ? "已标记为完成" : "已标记为未完成");
    } catch (error) {
      toast.error("操作失败");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-4">
      <div className="flex items-start gap-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleToggle}
          disabled={isLoading}
          className="mt-0.5 h-6 w-6 p-0"
        >
          {isCompleted ? (
            <CheckCircle2 className="h-5 w-5 text-green-600" />
          ) : (
            <Circle className="h-5 w-5 text-gray-400" />
          )}
        </Button>
        <div className="flex-1">
          <h3 className="font-medium text-sm mb-1">行动计划</h3>
          <p
            className={`text-sm ${
              isCompleted ? "line-through text-gray-500" : "text-gray-700"
            }`}
          >
            {action}
          </p>
        </div>
      </div>
    </Card>
  );
}
