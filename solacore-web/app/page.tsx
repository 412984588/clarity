import { SiteHeader } from "@/components/landing/site-header";
import { HeroSection } from "@/components/landing/hero-section";
import { TrustBadges } from "@/components/landing/trust-badges";
import { ProblemSection } from "@/components/landing/problem-section";
import { ProcessSection } from "@/components/landing/process-section";
import { FeaturesSection } from "@/components/landing/features-section";
import { UseCasesSection } from "@/components/landing/use-cases-section";
import { FAQSection } from "@/components/landing/faq-section";
import { CTASection } from "@/components/landing/cta-section";
import { SiteFooter } from "@/components/landing/site-footer";

// JSON-LD 结构化数据 - 帮助搜索引擎理解网站内容
const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "https://solacore.app/#website",
      url: "https://solacore.app",
      name: "Solacore",
      description: "AI 情绪梳理助手，把复杂的情绪转化为清晰的行动",
      inLanguage: "zh-CN",
    },
    {
      "@type": "SoftwareApplication",
      "@id": "https://solacore.app/#app",
      name: "Solacore",
      applicationCategory: "HealthApplication",
      operatingSystem: "Web, iOS, Android",
      description:
        "基于 CBT 认知行为疗法的 AI 情绪梳理助手。通过 5 步引导流程，帮你把复杂的情绪转化为清晰的行动计划。",
      offers: {
        "@type": "Offer",
        price: "0",
        priceCurrency: "CNY",
        availability: "https://schema.org/InStock",
      },
      aggregateRating: {
        "@type": "AggregateRating",
        ratingValue: "4.8",
        ratingCount: "128",
      },
    },
    {
      "@type": "Organization",
      "@id": "https://solacore.app/#organization",
      name: "Solacore",
      url: "https://solacore.app",
      logo: "https://solacore.app/logo.png",
      sameAs: [],
    },
  ],
};

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* JSON-LD 结构化数据 */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <SiteHeader />
      <main className="flex-1">
        <HeroSection />
        <TrustBadges />
        <ProblemSection />
        <ProcessSection />
        <FeaturesSection />
        <UseCasesSection />
        <FAQSection />
        <CTASection />
      </main>
      <SiteFooter />
    </div>
  );
}
