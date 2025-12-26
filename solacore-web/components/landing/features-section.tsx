import { BookOpen, Brain, MonitorSmartphone, ShieldCheck } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "情绪智能",
    desc: "AI 理解你的情绪状态，捕捉话语背后的真实需求。",
    tone: "bg-amber-100 text-amber-700",
  },
  {
    icon: ShieldCheck,
    title: "隐私保护",
    desc: "端到端加密与本地优先策略，让你的内容更安心。",
    tone: "bg-emerald-100 text-emerald-700",
  },
  {
    icon: MonitorSmartphone,
    title: "多端同步",
    desc: "手机、平板、电脑随时衔接，让思考不中断。",
    tone: "bg-sky-100 text-sky-700",
  },
  {
    icon: BookOpen,
    title: "科学方法",
    desc: "基于 CBT 认知行为疗法的 5 步引导流程。",
    tone: "bg-rose-100 text-rose-700",
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="bg-secondary/30 py-24">
      <div className="container mx-auto px-6">
        <div className="mx-auto mb-12 max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            温柔而专业的核心能力
          </h2>
          <p className="text-lg text-muted-foreground">
            既是情绪梳理助手，也是随身的心理教练。
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-2xl border bg-background/90 p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-md"
            >
              <div
                className={`mb-4 flex size-12 items-center justify-center rounded-2xl ${feature.tone}`}
              >
                <feature.icon className="size-6" />
              </div>
              <h3 className="text-lg font-semibold">{feature.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
