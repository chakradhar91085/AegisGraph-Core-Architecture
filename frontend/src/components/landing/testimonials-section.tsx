"use client";

import { useEffect, useState, useRef } from "react";

const TESTIMONIALS = [
  {
    quote: "JARVIS cut our agentic workflow build time from months to days. The orchestration layer is exactly what enterprise scale demands.",
    author: "Sarah Chen",
    role: "CTO",
    company: "MERIDIAN_LABS",
    metric: "12X",
    metricLabel: "FASTER DELIVERY",
  },
  {
    quote: "We run 8,000 concurrent research agents in production. JARVIS just handles it. Zero tuning, zero ops overhead.",
    author: "Marcus Webb",
    role: "Engineering Lead",
    company: "FLUX_SYSTEMS",
    metric: "8K",
    metricLabel: "AGENTS IN PROD",
  },
  {
    quote: "The audit trail alone was worth switching. Our compliance team can finally see exactly what every agent did and why.",
    author: "Elena Rodriguez",
    role: "VP Engineering",
    company: "BEACON_AI",
    metric: "100%",
    metricLabel: "AUDIT COVERAGE",
  },
  {
    quote: "Multi-agent reasoning was a black box before JARVIS. Now we trace every decision, every tool call. Absolute game changer.",
    author: "James Liu",
    role: "Founder",
    company: "PRISM_ANALYTICS",
    metric: "∞",
    metricLabel: "OBSERVABILITY",
  },
];

const LOGOS = [
  "MERIDIAN_LABS", "FLUX_SYSTEMS", "BEACON_AI", "PRISM_ANALYTICS",
  "NOVA_INTELLIGENCE", "QUANTUM_AGENTS", "ATLAS_DIGITAL", "VERTEX_AI_CO",
];

export function TestimonialsSection() {
  const [active, setActive] = useState(0);
  const [fading, setFading] = useState(false);
  const ref = useRef<HTMLElement>(null);
  const [vis, setVis] = useState(false);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVis(true); },
      { threshold: 0.1 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      setFading(true);
      setTimeout(() => {
        setActive(a => (a + 1) % TESTIMONIALS.length);
        setFading(false);
      }, 250);
    }, 5500);
    return () => clearInterval(id);
  }, []);

  const t = TESTIMONIALS[active];

  return (
    <section ref={ref} className="relative border-t border-[#1e1e1e]">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">

        {/* Header */}
        <div
          className={`border-b border-[#1e1e1e] py-8 flex items-end justify-between transition-all duration-500 ${vis ? "opacity-100" : "opacity-0"}`}
        >
          <span className="sys-tag">FIELD REPORTS</span>
          <span className="font-mono text-[10px] text-[#3a3a3a]">
            {String(active + 1).padStart(2, "0")} / {String(TESTIMONIALS.length).padStart(2, "0")}
          </span>
        </div>

        {/* Testimonial grid */}
        <div className="grid lg:grid-cols-[1fr_280px] border-b border-[#1e1e1e]">
          {/* Quote */}
          <div className="border-r border-[#1e1e1e] p-8 lg:p-12">
            <blockquote
              className={`transition-all duration-250 ${fading ? "opacity-0 translate-y-2" : "opacity-100 translate-y-0"}`}
            >
              <p className="font-display text-3xl lg:text-5xl leading-[0.95] tracking-tight text-[#f2ede6] mb-10">
                &ldquo;{t.quote}&rdquo;
              </p>
              <footer className="flex items-center gap-4">
                <div className="w-10 h-10 border border-[#2e2e2e] flex items-center justify-center bg-[#0e0e0e]">
                  <span className="font-display text-lg text-[#2196f3]">{t.author.charAt(0)}</span>
                </div>
                <div>
                  <p className="font-mono text-[11px] text-[#f2ede6] tracking-wider">{t.author}</p>
                  <p className="font-mono text-[10px] text-[#3a3a3a] tracking-wider">
                    {t.role} &nbsp;·&nbsp; {t.company}
                  </p>
                </div>
              </footer>
            </blockquote>
          </div>

          {/* Metric + nav */}
          <div className="flex flex-col">
            {/* Metric */}
            <div
              className={`flex-1 p-8 border-b border-[#1e1e1e] row-hover transition-all duration-250 ${fading ? "opacity-0" : "opacity-100"}`}
            >
              <span className="sys-tag text-[9px] mb-4 block">KEY_RESULT</span>
              <div className="font-display text-6xl text-[#2196f3]">{t.metric}</div>
              <div className="font-mono text-[10px] text-[#3a3a3a] tracking-widest mt-2">{t.metricLabel}</div>
            </div>

            {/* Nav dots */}
            <div className="p-6 flex items-center gap-2">
              {TESTIMONIALS.map((_, i) => (
                <button
                  key={i}
                  onClick={() => { setFading(true); setTimeout(() => { setActive(i); setFading(false); }, 250); }}
                  className={`h-1 transition-all duration-300 ${
                    i === active ? "w-8 bg-[#2196f3]" : "w-2 bg-[#2e2e2e] hover:bg-[#5a5a5a]"
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* Logo marquee — full viewport width */}
      <div className="border-t border-[#1e1e1e] py-5 overflow-hidden">
        <div className="marquee-fast flex gap-16 whitespace-nowrap">
          {[...Array(2)].map((_, ri) => (
            <span key={ri} className="inline-flex gap-16 shrink-0">
              {LOGOS.map(l => (
                <span key={`${l}-${ri}`} className="font-mono text-[11px] tracking-[0.2em] text-[#2e2e2e] hover:text-[#5a5a5a] transition-colors cursor-default">
                  {l}
                </span>
              ))}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
