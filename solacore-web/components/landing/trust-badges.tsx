import { HardDrive, ShieldCheck, Sparkles } from "lucide-react";

const badges = [
  {
    icon: ShieldCheck,
    label: "隐私优先",
    tone: "bg-emerald-100 text-emerald-700",
  },
  {
    icon: HardDrive,
    label: "本地存储",
    tone: "bg-amber-100 text-amber-700",
  },
  {
    icon: Sparkles,
    label: "AI驱动",
    tone: "bg-sky-100 text-sky-700",
  },
];

export function TrustBadges() {
  return (
    <section className="relative -mt-6 pb-12">
      <div className="container mx-auto px-6">
        <div className="grid gap-4 rounded-2xl border bg-background/80 p-6 shadow-sm backdrop-blur md:grid-cols-3">
          {badges.map((badge) => (
            <div
              key={badge.label}
              className="flex items-center justify-center gap-3 text-sm font-semibold text-foreground sm:justify-start"
            >
              <span
                className={`flex size-10 items-center justify-center rounded-xl ${badge.tone}`}
              >
                <badge.icon className="size-5" />
              </span>
              <span>{badge.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
