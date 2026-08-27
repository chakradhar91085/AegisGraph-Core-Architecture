"use client";

import { useEffect, useRef, useState } from "react";

import { AnimatedTetrahedron } from "./animated-tetrahedron";

const CONCEPTS = [
  {
    id: "01",
    tag: "TRACKING",
    title: "NODE EXPOSURE",
    desc: "AegisGraph tracks exactly which nodes in the knowledge graph have been exposed during the user's session.",
  },
  {
    id: "02",
    tag: "AWARENESS",
    title: "NEW ACTIVATIONS",
    desc: "Visually distinguish between previously known context and newly activated paths uncovered by the latest query.",
  },
  {
    id: "03",
    tag: "MONITORING",
    title: "EXPLORATION SPREAD",
    desc: "Watch how information retrieval cascades through the graph, revealing potential structural vulnerabilities in real time.",
  },
  {
    id: "04",
    tag: "ENFORCEMENT",
    title: "ADAPTIVE BOUNDARIES",
    desc: "As behavioral risk increases, the system dynamically restricts the reachable subgraph, preventing dangerous deep traversal.",
  },
];

export function SecuritySection() {
  const [vis, setVis] = useState(false);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVis(true); },
      { threshold: 0.1 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <section id="security" ref={ref} className="relative border-t border-[#1e1e1e] bg-[#080808] scroll-mt-[88px]">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">

        {/* Header row */}
        <div
          className={`border-b border-[#1e1e1e] py-8 flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 transition-all duration-500 ${vis ? "opacity-100" : "opacity-0"}`}
        >
          <div>
            <span className="sys-tag mb-3 block">GRAPH EXPLORATION</span>
            <h2 className="font-display text-6xl lg:text-8xl leading-[0.88] tracking-tight text-[#f2ede6]">
              VISUALIZE
              <br />
              <span style={{ WebkitTextStroke: "1px #3a3a3a", color: "transparent" }}>THE BOUNDARY</span>
            </h2>
          </div>
          </div>

        {/* Feature grid */}
        <div className="grid lg:grid-cols-2 border-b border-[#1e1e1e]">
          
          {/* Left Side: 3D Visualization */}
          <div className="border-r border-[#1e1e1e] p-0 h-[400px] lg:h-auto relative bg-[#050505]">
            <AnimatedTetrahedron />
            <div className="absolute top-6 left-6 flex items-center gap-2 pointer-events-none">
              <span className="w-1.5 h-1.5 rounded-full bg-[#2196f3] animate-pulse" />
              <span className="font-mono text-[9px] tracking-widest text-[#5a5a5a]">RESTRICTED SUBGRAPH</span>
            </div>
          </div>

          {/* Right Side: Text Cards */}
          <div className="grid md:grid-cols-2">
            {CONCEPTS.map((c, i) => (
              <div
                key={c.id}
                className={`border-b md:border-b-0 md:[&:nth-child(1)]:border-b md:[&:nth-child(2)]:border-b border-[#1e1e1e] p-6 row-hover transition-all duration-500 group ${
                  i % 2 === 0 ? "border-r" : ""
                } ${vis ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}`}
                style={{ transitionDelay: `${i * 80}ms` }}
              >
                <div className="flex items-center justify-between mb-8">
                  <span className="sys-tag text-[9px]">{c.tag}</span>
                  <span className="font-mono text-[9px] text-[#2e2e2e]">{c.id}</span>
                </div>
                <h3 className="font-display text-2xl leading-[0.9] text-[#f2ede6] mb-3 group-hover:text-[#2196f3] transition-colors">
                  {c.title}
                </h3>
                <p className="text-sm text-[#5a5a5a] leading-relaxed">{c.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom note */}
        <div className="py-5 flex items-center justify-between">
          <span className="font-mono text-[10px] text-[#3a3a3a]">
            VISUALLY TRACK GRAPH-RAG EXPLORATION PATHS
          </span>
          <a href="#" className="font-mono text-[10px] text-[#2196f3] hover:underline tracking-wider">
            INTERACTIVE DEMO →
          </a>
        </div>
      </div>
    </section>
  );
}
