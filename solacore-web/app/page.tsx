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

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
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
