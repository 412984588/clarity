import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";

export function CTASection() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-amber-50 via-white to-emerald-50" />
      <div className="container mx-auto px-6">
        <div className="mx-auto flex max-w-3xl flex-col items-center gap-6 text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            准备好找回内心的平静了吗？
          </h2>
          <p className="text-lg text-muted-foreground">
            从今天开始，给自己一个更清晰、更温柔的答案。
          </p>
          <Button
            asChild
            size="lg"
            className="h-12 rounded-full px-10 text-base"
          >
            <Link href="/register">
              免费开始
              <ArrowRight className="ml-2 size-4" />
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
