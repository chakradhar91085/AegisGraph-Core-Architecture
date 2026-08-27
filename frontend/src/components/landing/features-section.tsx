"use client";

import { useEffect, useRef, useState } from "react";

const FEATURES = [
  {
    id: "01",
    tag: "ANALYSIS",
    title: "BEHAVIORAL\nRISK",
    desc: "Evaluate query sequences rather than treating every request independently. AegisGraph detects when seemingly harmless queries combine into targeted reconnaissance.",
    stat: { v: "EWMA", l: "risk scoring" },
  },
  {
    id: "02",
    tag: "MONITORING",
    title: "ENTITY\nEXPLORATION",
    desc: "Detect focused exploration of specific people, organizations, entities, or graph regions. Track the semantic drift and concentration of a user's session.",
    stat: { v: "O(1)", l: "telemetry overhead" },
  },
  {
    id: "03",
    tag: "CONTROL",
    title: "ADAPTIVE\nACCESS",
    desc: "Dynamically reduce accessible graph depth and retrieval context as behavioral risk increases. Prevent deep traversal without breaking legitimate shallow queries.",
    stat: { v: "0-4", l: "dynamic depth range" },
  },
  {
    id: "04",
    tag: "SECURITY",
    title: "SECURE\nRETRIEVAL",
    desc: "Ensure retrieval is mediated by the security and policy layer. The local LLM never sees information that violates the active behavioral policy.",
    stat: { v: "100%", l: "policy enforcement" },
  },
  {
    id: "05",
    tag: "VISUALIZATION",
    title: "EXPLORATION\nVISUALIZATION",
    desc: "Visualize the exact portion of the knowledge graph being explored during a session. See what the user sees, and how the policy restricts their view.",
    stat: { v: "D3", l: "force-directed layout" },
  },
  {
    id: "06",
    tag: "AUDITING",
    title: "SECURITY\nTELEMETRY",
    desc: "Expose risk evolution and behavioral signals for analysis and auditing. Export complete forensic trails of how the graph was explored.",
    stat: { v: "JSON", l: "telemetry payloads" },
  },
];

function FeatureRow({ f, index }: { f: typeof FEATURES[0]; index: number }) {
  const [vis, setVis] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVis(true); },
      { threshold: 0.15 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`group border-b border-[#1e1e1e] transition-all duration-500 row-hover ${
        vis ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
      }`}
      style={{ transitionDelay: `${index * 80}ms` }}
    >
      <div className="grid grid-cols-[56px_1fr] lg:grid-cols-[56px_260px_1fr_160px] gap-0">
        {/* Number col */}
        <div className="border-r border-[#1e1e1e] p-5 flex items-start pt-6">
          <span className="font-mono text-[10px] text-[#3a3a3a] tracking-widest">{f.id}</span>
        </div>

        {/* Tag + Title */}
        <div className="border-r border-[#1e1e1e] p-6 flex flex-col gap-3">
          <span className="sys-tag text-[9px]">{f.tag}</span>
          <h3 className="font-display text-3xl lg:text-4xl leading-[0.9] text-[#f2ede6] group-hover:text-[#2196f3] transition-colors duration-300 whitespace-pre-line">
            {f.title}
          </h3>
        </div>

        {/* Description */}
        <div className="col-span-2 lg:col-span-1 border-r border-[#1e1e1e] p-6 flex items-center">
          <p className="text-sm text-[#5a5a5a] leading-relaxed max-w-lg">{f.desc}</p>
        </div>

        {/* Stat */}
        <div className="hidden lg:flex flex-col items-end justify-center p-6">
          <div className="font-display text-4xl text-[#2196f3]">{f.stat.v}</div>
          <div className="font-mono text-[9px] text-[#3a3a3a] tracking-widest mt-1 text-right">{f.stat.l}</div>
        </div>
      </div>
    </div>
  );
}

export function FeaturesSection() {
  const [vis, setVis] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVis(true); },
      { threshold: 0.05 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <section id="features" className="relative border-t border-[#1e1e1e] scroll-mt-[88px]">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        {/* Section header row */}
        <div
          ref={ref}
          className={`grid grid-cols-[56px_1fr] lg:grid-cols-[56px_260px_1fr_160px] border-b border-[#1e1e1e] transition-all duration-500 ${
            vis ? "opacity-100" : "opacity-0"
          }`}
        >
          <div className="border-r border-[#1e1e1e] p-5" />
          <div className="col-span-2 lg:col-span-3 p-6 flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
            <div>
              <span className="sys-tag mb-4 block">CAPABILITIES</span>
              <h2 className="font-display text-6xl lg:text-8xl text-[#f2ede6] leading-[0.88] tracking-tight">
                AEGISGRAPH<br />
                <span className="text-[#3a3a3a]" style={{ WebkitTextStroke: "1px #3a3a3a", color: "transparent" }}>
                  CAPABILITIES
                </span>
              </h2>
            </div>
            <p className="font-mono text-[10px] text-[#3a3a3a] tracking-widest max-w-[200px] text-right hidden lg:block">
              SIX CORE MODULES &nbsp;/ &nbsp;RESEARCH-GRADE &nbsp;/ &nbsp;GRAPH-RAG SECURITY
            </p>
          </div>
        </div>

        {/* Feature rows */}
        {FEATURES.map((f, i) => (
          <FeatureRow key={f.id} f={f} index={i} />
        ))}

        {/* CTA row */}
        <div className="grid grid-cols-[56px_1fr] border-b border-[#1e1e1e]">
          <div className="border-r border-[#1e1e1e]" />
          <div className="p-6 flex items-center justify-between">
            <span className="font-mono text-[10px] text-[#3a3a3a]">VIEW ALL CAPABILITIES IN DOCS →</span>
            <a href="#" className="font-mono text-xs text-[#2196f3] hover:underline tracking-wider">READ RESEARCH PAPER</a>
          </div>
        </div>
      </div>
    </section>
  );
}
