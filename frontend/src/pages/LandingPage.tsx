import { Navigation } from '../components/landing/navigation';
import { HeroSection } from '../components/landing/hero-section';
import { FeaturesSection } from '../components/landing/features-section';
import { HowItWorksSection } from '../components/landing/how-it-works-section';
import { MetricsSection } from '../components/landing/metrics-section';
import { SecuritySection } from '../components/landing/security-section';
import { CtaSection } from '../components/landing/cta-section';
import { FooterSection } from '../components/landing/footer-section';

export function LandingPage() {
  return (
    <main className="relative min-h-screen overflow-x-hidden bg-[#050505]">
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <MetricsSection />
      <SecuritySection />
      <CtaSection />
      <FooterSection />
    </main>
  );
}
