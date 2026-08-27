"use client";

import { useEffect, useRef, useState } from "react";

const STEPS = [
  {
    id: "01",
    tag: "EXPLORE",
    title: "USER\nQUERY",
    desc: "The user explores the knowledge graph through natural language. They might start with a seemingly harmless question about a person or project.",
    code: `{\n  "event": "query_received",\n  "query": "Who is Veronica Espinoza?",\n  "timestamp": "2026-08-24T10:01:45Z"\n}`,
  },
  {
    id: "02",
    tag: "OBSERVE",
    title: "BEHAVIORAL\nANALYSIS",
    desc: "The system continuously observes exploration patterns—tracking entity focus, repeated probing, and graph traversal behavior over the course of the session.",
    code: `{\n  "event": "behavior_analysis",\n  "entity_focus_score": 0.42,\n  "repeated_probing": false,\n  "recent_queries": 3\n}`,
  },
  {
    id: "03",
    tag: "SCORE",
    title: "RISK\nASSESSMENT",
    desc: "Behavioral signals are aggregated into a continuous Exponentially Weighted Moving Average (EWMA) risk score, quantifying the likelihood of targeted reconnaissance.",
    code: `{\n  "event": "risk_calculated",\n  "raw_ewma_score": 0.58,\n  "risk_delta": "+0.15",\n  "threshold_status": "ELEVATED"\n}`,
  },
  {
    id: "04",
    tag: "ENFORCE",
    title: "ADAPTIVE\nPOLICY",
    desc: "Based on the dynamic risk score, the Adaptive Policy kicks in. It determines the maximum permissible graph traversal depth and context limits for this specific query.",
    code: `{\n  "event": "policy_evaluated",\n  "risk_level": "MEDIUM",\n  "permitted_depth": 2,\n  "context_limit": 15\n}`,
  },
  {
    id: "05",
    tag: "RETRIEVE",
    title: "SECURE GRAPH\nRETRIEVAL",
    desc: "The Retrieval Service queries Neo4j, strictly adhering to the policy bounds. If the user's risk is high, deep relationships are mathematically unreachable.",
    code: `{\n  "event": "graph_retrieval",\n  "nodes_extracted": 12,\n  "edges_extracted": 14,\n  "policy_enforced": true\n}`,
  },
  {
    id: "06",
    tag: "RESPOND",
    title: "AI\nRESPONSE",
    desc: "The local LLM generates an answer grounded entirely within the policy-authorized subgraph. The AI cannot leak what it is never given.",
    code: `{\n  "event": "generation_complete",\n  "model": "qwen2.5-coder:7b",\n  "grounding_score": 0.98,\n  "status": "SECURE"\n}`,
  },
];

export function HowItWorksSection() {
  const [active, setActive]   = useState(0);
  const [vis, setVis]         = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVis(true); },
      { threshold: 0.1 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    const id = setInterval(() => setActive(a => (a + 1) % STEPS.length), 5000);
    return () => clearInterval(id);
  }, []);

  const step = STEPS[active];

  return (
    <section id="how-it-works" ref={ref} className="relative border-t border-[#1e1e1e] bg-[#080808] scroll-mt-[88px]">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">

        {/* Header row */}
        <div
          className={`border-b border-[#1e1e1e] py-8 flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 transition-all duration-500 ${vis ? "opacity-100" : "opacity-0"}`}
        >
          <div>
            <span className="sys-tag mb-3 block">PROCESS</span>
            <h2 className="font-display text-6xl lg:text-8xl leading-[0.88] tracking-tight text-[#f2ede6]">
              SHIP IN<br />
              <span style={{ WebkitTextStroke: "1px #3a3a3a", color: "transparent" }}>THREE STEPS</span>
            </h2>
          </div>
          <span className="font-mono text-[10px] text-[#3a3a3a] tracking-widest">
            EXPLORE &nbsp;·&nbsp; ANALYZE &nbsp;·&nbsp; SECURE
          </span>
        </div>

        {/* Main grid */}
        <div className="grid lg:grid-cols-[280px_1fr] border-b border-[#1e1e1e]">
          {/* Step nav */}
          <div className="border-r border-[#1e1e1e]">
            {STEPS.map((s, i) => (
              <button
                key={s.id}
                onClick={() => setActive(i)}
                className={`w-full text-left border-b border-[#1e1e1e] p-6 transition-all duration-200 group ${
                  active === i ? "bg-[#0e0e0e]" : "hover:bg-[#0a0a0a]"
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono text-[9px] text-[#3a3a3a] tracking-widest">{s.tag}</span>
                  <span className="font-mono text-[10px] text-[#3a3a3a]">{s.id}</span>
                </div>
                <h3 className={`font-display text-2xl leading-[0.9] transition-colors ${
                  active === i ? "text-[#2196f3]" : "text-[#3a3a3a] group-hover:text-[#5a5a5a]"
                }`}>
                  {s.title}
                </h3>
                {/* Progress bar */}
                {active === i && (
                  <div className="mt-4 h-px bg-[#1e1e1e] overflow-hidden">
                    <div
                      key={active}
                      className="h-full bg-[#2196f3]"
                      style={{ width: 0, animation: "draw-line 5s linear forwards" }}
                    />
                  </div>
                )}
              </button>
            ))}
          </div>

          {/* Content panel */}
          <div className="grid lg:grid-cols-2">
            {/* Description */}
            <div className="border-r border-[#1e1e1e] p-8 flex flex-col justify-between">
              <div>
                <p className="text-sm text-[#5a5a5a] leading-relaxed mb-8">{step.desc}</p>
                <a href="#" className="inline-flex items-center gap-2 font-mono text-[11px] text-[#2196f3] tracking-wider hover:underline">
                  READ DOCS →
                </a>
              </div>
              <div className="mt-8 font-mono text-[10px] text-[#3a3a3a] border-t border-[#1e1e1e] pt-4 uppercase">
                STAGE &nbsp;{step.id} &nbsp;OF &nbsp;06
              </div>
            </div>

            {/* Code block */}
            <div className="bg-[#050505]">
              {/* Code header */}
              <div className="border-b border-[#1e1e1e] px-5 py-3 flex items-center justify-between">
                <span className="font-mono text-[10px] text-[#3a3a3a]">telemetry_event.json</span>
                <div className="flex items-center gap-2">
                  <span className="status-pulse w-1.5 h-1.5 rounded-full bg-[#22c55e] inline-block" />
                  <span className="font-mono text-[10px] text-[#22c55e]">READY</span>
                </div>
              </div>
              {/* Code lines */}
              <div className="p-6 font-mono text-[12px] min-h-[260px]">
                <pre>
                  {step.code.split("\n").map((line, li) => (
                    <div
                      key={`${active}-${li}`}
                      className="leading-7"
                      style={{ animation: `fade-up 0.3s ease ${li * 60}ms both` }}
                    >
                      <span className="text-[#3a3a3a] select-none w-5 inline-block text-right mr-4">
                        {li + 1}
                      </span>
                      <span className="text-[#5a5a5a]">{line}</span>
                    </div>
                  ))}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
