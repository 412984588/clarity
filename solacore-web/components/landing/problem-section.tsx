import { CloudFog, Scale, Shuffle } from "lucide-react";

const problems = [
  {
    icon: Shuffle,
    title: "选择困难",
    desc: "太多选项，怕选错",
    tone: "bg-amber-100 text-amber-700",
  },
  {
    icon: CloudFog,
    title: "情绪迷雾",
    desc: "压力大到无法思考",
    tone: "bg-sky-100 text-sky-700",
  },
  {
    icon: Scale,
    title: "缺乏客观",
    desc: "朋友建议带有偏见",
    tone: "bg-emerald-100 text-emerald-700",
  },
];

export function ProblemSection() {
  return (
    <section className="relative py-24">
      <div className="absolute inset-0 -z-10">
        <div className="absolute left-0 top-16 h-40 w-40 rounded-full bg-amber-100/50 blur-3xl" />
        <div className="absolute bottom-10 right-10 h-52 w-52 rounded-full bg-emerald-100/40 blur-3xl" />
      </div>

      <div className="container mx-auto px-6">
        <div className="mx-auto mb-12 max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            你是否也有这样的困扰？
          </h2>
          <p className="text-lg text-muted-foreground">
            情绪卡住的瞬间，我们需要更清晰的判断，而不是更多的噪音。
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {problems.map((problem) => (
            <div
              key={problem.title}
              className="group rounded-2xl border bg-card/80 p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-md"
            >
              <div className="flex items-center gap-4">
                <div
                  className={`flex size-12 items-center justify-center rounded-2xl ${problem.tone}`}
                >
                  <problem.icon className="size-6" />
                </div>
                <h3 className="text-lg font-semibold">{problem.title}</h3>
              </div>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                {problem.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
