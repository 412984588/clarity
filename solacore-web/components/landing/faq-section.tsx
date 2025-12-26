"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

const faqs = [
  {
    question: "Solacore 是什么？",
    answer:
      "Solacore 是一款情绪梳理与决策辅助的心理教练 App，提供基于 CBT 的 5 步引导，让你在情绪中找到清晰行动。",
  },
  {
    question: "和心理咨询有什么区别？",
    answer:
      "Solacore 更像随时可用的日常教练，帮助你整理想法与情绪，不替代专业心理咨询。如有严重困扰，仍建议寻求专业帮助。",
  },
  {
    question: "我的数据安全吗？",
    answer:
      "我们坚持隐私优先策略，内容以本地存储为主，并提供加密保护与一键删除选项。",
  },
  {
    question: "是否收费？",
    answer: "目前可免费开始体验，未来如推出高级功能会提前告知，你可按需选择。",
  },
];

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="bg-secondary/30 py-24">
      <div className="container mx-auto px-6">
        <div className="mx-auto mb-12 max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            常见问题
          </h2>
          <p className="text-lg text-muted-foreground">
            关于 Solacore 的关键疑问，我们都先替你回答。
          </p>
        </div>

        <div className="mx-auto flex max-w-3xl flex-col gap-4">
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index;
            return (
              <div
                key={faq.question}
                className="rounded-2xl border bg-background/90 p-6 shadow-sm transition duration-300 hover:shadow-md"
              >
                <button
                  type="button"
                  className="flex w-full items-center justify-between gap-6 text-left"
                  aria-expanded={isOpen}
                  aria-controls={`faq-panel-${index}`}
                  onClick={() => setOpenIndex(isOpen ? null : index)}
                >
                  <span className="text-lg font-semibold">{faq.question}</span>
                  <ChevronDown
                    className={`size-5 text-muted-foreground transition-transform ${
                      isOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>
                <div
                  id={`faq-panel-${index}`}
                  className="grid transition-all duration-300 ease-out"
                  style={{ gridTemplateRows: isOpen ? "1fr" : "0fr" }}
                >
                  <div className="overflow-hidden">
                    <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
