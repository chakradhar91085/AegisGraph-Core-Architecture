"use client";

import { useEffect, useState } from "react";
import { AgentParticleCanvas } from "./agent-particle-canvas";
import { SignedIn, SignedOut, SignInButton } from "@clerk/clerk-react";
import { ShieldCheck, Network, Eye, BrainCircuit } from "lucide-react";

const VERBS = ["Retrieves", "Explores", "Connects", "Protects"];



export function HeroSection() {
  const [verbIdx, setVerbIdx] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => { setVisible(true); }, []);

  useEffect(() => {
    const id = setInterval(() => setVerbIdx(v => (v + 1) % VERBS.length), 3500);
    return () => clearInterval(id);
  }, []);

  return (
    <section className="relative min-h-screen flex flex-col justify-center overflow-x-hidden grid-bg pt-[88px]">
      {/* Particle canvas — right half of hero, full height, behind content */}
      <div className="absolute inset-y-0 right-0 w-full lg:w-[55%] pointer-events-none z-0">
        <AgentParticleCanvas className="w-full h-full" />
      </div>
      {/* Blue radial glow — reinforces canvas area */}
      <div
        className="absolute inset-0 pointer-events-none z-0"
        style={{ background: "radial-gradient(ellipse 50% 60% at 80% 50%, rgba(33,150,243,0.06) 0%, transparent 70%)" }}
      />

      <div className="relative z-20 max-w-[1400px] mx-auto px-6 lg:px-12 py-20 lg:py-28 w-full">



        {/* ── MAIN LAYOUT ─── */}
        <div className="grid lg:grid-cols-[50%_50%] gap-8 lg:gap-12 items-center min-h-[75vh]">

          {/* LEFT COLUMN */}
          <div className="relative z-10 pt-10 lg:pr-8">
            {/* Giant headline */}
            <div
              className={`transition-all duration-700 delay-100 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}`}
            >
              {/* Line 1 */}
              <div className="overflow-hidden mb-6">
                <div className="inline-flex items-center gap-2 border border-[#2196f3]/30 bg-[#2196f3]/10 px-3 py-1.5 rounded-full">
                  <ShieldCheck className="w-4 h-4 text-[#2196f3]" />
                  <p className="font-mono text-[11px] tracking-[0.2em] text-[#2196f3] font-bold">
                    AI + GRAPH + SECURITY
                  </p>
                </div>
              </div>

              {/* Big headline */}
              <h1 className="font-display not-italic text-4xl sm:text-5xl lg:text-[56px] leading-[1.1] tracking-tight text-[#f2ede6]">
                Securing How AI
              </h1>
              {/* Container inherits font size so h-[1.5em] calculates correctly without clipping */}
              <div className="relative font-display text-4xl sm:text-5xl lg:text-[56px] leading-[1.1] h-[1.5em] mt-1 pt-1 overflow-visible">
                {VERBS.map((verb, idx) => (
                  <div
                    key={verb}
                    className={`absolute left-0 top-1 whitespace-nowrap transition-all duration-700 ease-out flex items-center
                      ${idx === verbIdx ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-4 pointer-events-none"}`}
                  >
                    <span 
                      className="tracking-tight not-italic"
                      style={{ WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundImage: "linear-gradient(to right, #2196f3, #8b5cf6)" }}
                    >
                      {verb}
                    </span>
                    {/* Blinking cursor matching the reference image */}
                    <span className="ml-1 w-[4px] h-[0.9em] bg-[#2196f3] opacity-80 animate-pulse"></span>
                  </div>
                ))}
              </div>
            </div>

            {/* Subtext */}
            <div
              className={`mt-6 lg:mt-8 transition-all duration-700 delay-300 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}
            >
              <p className="text-sm sm:text-base lg:text-lg text-[#8a8a8a] leading-relaxed max-w-lg">
                AegisGraph adds a behavioral security layer to Graph-RAG systems, detecting probing behavior, controlling access, and protecting enterprise knowledge.
              </p>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-3 mt-8 w-fit">
                <SignedOut>
                  <SignInButton mode="modal" forceRedirectUrl="/app">
                    <button className="group inline-flex items-center gap-8 bg-[#2196f3] text-[#050505] font-mono text-sm tracking-widest px-6 py-4 hover:bg-[#42a5f5] transition-colors font-semibold whitespace-nowrap cursor-pointer">
                      SIGN IN TO LAUNCH
                      <span className="transition-transform group-hover:translate-x-1">→</span>
                    </button>
                  </SignInButton>
                </SignedOut>
                <SignedIn>
                  <a
                    href="/app"
                    className="group inline-flex items-center gap-8 bg-[#2196f3] text-[#050505] font-mono text-sm tracking-widest px-6 py-4 hover:bg-[#42a5f5] transition-colors font-semibold whitespace-nowrap"
                  >
                    LAUNCH AEGISGRAPH
                    <span className="transition-transform group-hover:translate-x-1">→</span>
                  </a>
                </SignedIn>
                <a
                  href="#"
                  className="group inline-flex items-center gap-8 border border-[#1e1e1e] text-[#f2ede6] font-mono text-sm tracking-widest px-6 py-4 hover:border-[#2196f3]/40 hover:text-[#2196f3] transition-colors whitespace-nowrap"
                >
                  READ RESEARCH
                  <span className="transition-transform group-hover:translate-x-1">→</span>
                </a>
              </div>

              {/* Features row */}
              <div className={`mt-16 grid grid-cols-2 lg:grid-cols-4 gap-6 pt-6 transition-all duration-700 delay-500 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
                
                <div className="flex flex-col gap-3">
                  <ShieldCheck className="w-6 h-6 text-[#2196f3]" />
                  <h4 className="text-sm font-semibold text-[#f2ede6]">Behavior Detection</h4>
                  <p className="text-xs text-[#8a8a8a] leading-relaxed">Spot suspicious patterns in real time</p>
                </div>

                <div className="flex flex-col gap-3 lg:border-l lg:border-[#1e1e1e] lg:pl-6">
                  <Network className="w-6 h-6 text-[#2196f3]" />
                  <h4 className="text-sm font-semibold text-[#f2ede6]">Access Control</h4>
                  <p className="text-xs text-[#8a8a8a] leading-relaxed">Limit information exposure dynamically</p>
                </div>

                <div className="flex flex-col gap-3 lg:border-l lg:border-[#1e1e1e] lg:pl-6">
                  <Eye className="w-6 h-6 text-[#2196f3]" />
                  <h4 className="text-sm font-semibold text-[#f2ede6]">Graph Protection</h4>
                  <p className="text-xs text-[#8a8a8a] leading-relaxed">Prevent data leakage and reconstruction</p>
                </div>

                <div className="flex flex-col gap-3 lg:border-l lg:border-[#1e1e1e] lg:pl-6">
                  <BrainCircuit className="w-6 h-6 text-[#2196f3]" />
                  <h4 className="text-sm font-semibold text-[#f2ede6]">Enterprise Ready</h4>
                  <p className="text-xs text-[#8a8a8a] leading-relaxed">Built for secure AI workflows</p>
                </div>

              </div>
            </div>
          </div>
        </div>

      </div>

      {/* ── BOTTOM TICKER — full viewport width ─── */}
      <div
        className={`absolute bottom-0 left-0 right-0 border-t border-[#1e1e1e] py-5 transition-all duration-700 delay-700 ${visible ? "opacity-100" : "opacity-0"}`}
      >
        <div className="overflow-hidden">
          <div className="marquee-fast whitespace-nowrap flex gap-16">
            {[...Array(2)].map((_, rep) => (
              <span key={rep} className="inline-flex items-center gap-16">
                {[
                  "BEHAVIORAL RISK MODELING",
                  "ADAPTIVE POLICY ENFORCEMENT",
                  "ENTITY FOCUS TRACKING",
                  "GRAPH DEPTH LIMITATION",
                  "SECURE CONTEXT RETRIEVAL",
                  "GRAPH-RAG SECURITY",
                  "KNOWLEDGE GRAPH MONITORING",
                ].map(item => (
                  <span key={item} className="flex items-center gap-3 font-mono text-[10px] tracking-[0.2em] text-[#3a3a3a]">
                    <span className="w-1 h-1 bg-[#2196f3] inline-block shrink-0" />
                    {item}
                  </span>
                ))}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
