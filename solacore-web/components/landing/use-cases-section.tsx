import { Briefcase, Compass, HeartHandshake } from "lucide-react";

const useCases = [
  {
    icon: Briefcase,
    title: "职场困境",
    desc: "遇到难缠的同事或老板，如何保持边界与效率？",
    tone: "bg-amber-100 text-amber-700",
  },
  {
    icon: HeartHandshake,
    title: "关系抉择",
    desc: "要不要分手或和好，怎么厘清真实需求？",
    tone: "bg-rose-100 text-rose-700",
  },
  {
    icon: Compass,
    title: "人生选择",
    desc: "换工作、搬家或重大决定，需要更清晰的方向感。",
    tone: "bg-emerald-100 text-emerald-700",
  },
];

export function UseCasesSection() {
  return (
    <section className="relative py-24">
      <div className="absolute inset-0 -z-10">
        <div className="absolute left-10 top-20 h-48 w-48 rounded-full bg-sky-100/50 blur-3xl" />
        <div className="absolute bottom-8 right-8 h-56 w-56 rounded-full bg-amber-100/40 blur-3xl" />
      </div>

      <div className="container mx-auto px-6">
        <div className="mx-auto mb-12 max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            Solacore 能帮你解决
          </h2>
          <p className="text-lg text-muted-foreground">
            把情绪拆解成问题，再把问题变成行动。
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {useCases.map((useCase) => (
            <div
              key={useCase.title}
              className="rounded-2xl border bg-card/80 p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-md"
            >
              <div
                className={`mb-4 flex size-12 items-center justify-center rounded-2xl ${useCase.tone}`}
              >
                <useCase.icon className="size-6" />
              </div>
              <h3 className="text-lg font-semibold">{useCase.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                {useCase.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
