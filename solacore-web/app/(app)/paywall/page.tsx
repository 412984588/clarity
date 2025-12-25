import { Check } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const plans = [
  {
    id: "free",
    name: "Free",
    price: "￥0",
    description: "体验五步结构化思考",
    features: ["每月 5 次对话", "基础情绪记录", "标准支持"],
  },
  {
    id: "standard",
    name: "Standard",
    price: "￥68/月",
    description: "为持续成长准备",
    features: ["无限对话", "深度选项卡片", "会话回顾", "优先支持"],
    highlight: true,
  },
  {
    id: "pro",
    name: "Pro",
    price: "￥128/月",
    description: "团队与长期计划",
    features: ["团队协作", "高级洞察报告", "专属顾问", "API 接入"],
  },
];

export default function PaywallPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
          选择订阅
        </p>
        <h1 className="text-3xl font-semibold">升级你的清晰度工具箱</h1>
        <p className="text-sm text-muted-foreground">
          选择适合你的方案，把每一次对话转化成行动。
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        {plans.map((plan) => (
          <Card
            key={plan.id}
            className={cn(
              "relative overflow-hidden",
              plan.highlight && "border-foreground shadow-lg",
            )}
          >
            {plan.highlight ? (
              <span className="absolute right-4 top-4 rounded-full bg-foreground px-3 py-1 text-xs text-background">
                推荐
              </span>
            ) : null}
            <CardHeader className="space-y-2">
              <CardTitle className="text-xl">{plan.name}</CardTitle>
              <p className="text-3xl font-semibold">{plan.price}</p>
              <p className="text-sm text-muted-foreground">
                {plan.description}
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2 text-sm text-muted-foreground">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2">
                    <Check className="mt-0.5 size-4 text-foreground" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <Button
                className="w-full"
                variant={plan.highlight ? "default" : "outline"}
              >
                订阅 {plan.name}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
