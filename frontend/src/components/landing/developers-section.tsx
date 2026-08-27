"use client";

import { useState, useEffect, useRef } from "react";
import { Copy, Check } from "lucide-react";

const TABS = [
  {
    label: "INSTALL",
    code: `# npm
npm install @jarvis/sdk

# pnpm
pnpm add @jarvis/sdk

# yarn
yarn add @jarvis/sdk`,
  },
  {
    label: "CREATE",
    code: `import { jarvis } from '@jarvis/sdk'

const agent = jarvis.agent({
  name: 'data-analyst',
  model: 'claude-opus-4',
  tools: ['db.query', 'code.run'],
  memory: { scope: 'persistent' }
})

const result = await agent.run(
  'Analyze Q2 revenue trends'
)
// → runs autonomously, returns report`,
  },
  {
    label: "ORCHESTRATE",
    code: `const pipeline = jarvis.workflow({
  agents: [researcher, analyst, writer],
  strategy: 'parallel',
  onComplete: async (results) => {
    await jarvis.notify(results)
  },
  timeout: '10m',
})

const run = await pipeline.execute(task)
// → 3 agents · 4.2s · $0.003 cost`,
  },
  {
    label: "OBSERVE",
    code: `// Stream agent thoughts in real time
const stream = jarvis.stream(agentId)

stream.on('thought',  (t) => console.log(t))
stream.on('tool_use', (t) => logTool(t))
stream.on('complete', (r) => save(r))

// Query audit trail
const logs = await jarvis.audit({
  agentId,
  from: '2025-04-01',
  actions: ['tool_call', 'api_request'],
})`,
  },
];

const SDK_PROPS = [
  { k: "TypeScript native",  v: "Full type-safety, auto-generated types from your schema." },
  { k: "Streaming output",   v: "Real-time agent thoughts via SSE and WebSockets." },
  { k: "Edge-compatible",    v: "Node, Deno, Bun, Cloudflare Workers, Vercel Edge." },
  { k: "8KB gzipped",        v: "Lightweight core. Tree-shakeable plugins." },
];

export function DevelopersSection() {
  const [tab, setTab]     = useState(0);
  const [copied, setCopied] = useState(false);
  const [vis, setVis]     = useState(false);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVis(true); },
      { threshold: 0.1 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  const copy = () => {
    navigator.clipboard.writeText(TABS[tab].code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="developers" ref={ref} className="relative border-t border-[#1e1e1e] scroll-mt-[88px]">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">

        {/* Header row */}
        <div
          className={`border-b border-[#1e1e1e] py-8 transition-all duration-500 ${vis ? "opacity-100" : "opacity-0"}`}
        >
          <span className="sys-tag mb-3 block">DEVELOPER SDK</span>
          <h2 className="font-display text-6xl lg:text-8xl leading-[0.88] tracking-tight text-[#f2ede6]">
            BUILT FOR<br />
            <span style={{ WebkitTextStroke: "1px #3a3a3a", color: "transparent" }}>BUILDERS</span>
          </h2>
        </div>

        <div className="grid lg:grid-cols-2 border-b border-[#1e1e1e]">
          {/* Left — SDK properties */}
          <div className="border-r border-[#1e1e1e]">
            <div className="border-b border-[#1e1e1e] p-6">
              <p className="text-sm text-[#5a5a5a] leading-relaxed max-w-md">
                A zero-friction SDK to spawn, orchestrate, and observe agents in production. Ship your first autonomous workflow in under 10 minutes.
              </p>
            </div>

            {SDK_PROPS.map((p, i) => (
              <div
                key={p.k}
                className={`border-b border-[#1e1e1e] px-6 py-5 row-hover transition-all duration-400 ${
                  vis ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-4"
                }`}
                style={{ transitionDelay: `${i * 60 + 100}ms` }}
              >
                <div className="flex items-start justify-between gap-4">
                  <span className="font-mono text-[11px] text-[#2196f3] tracking-wider">{p.k}</span>
                  <span className="font-mono text-[10px] text-[#3a3a3a]">{String(i + 1).padStart(2, "0")}</span>
                </div>
                <p className="mt-1 text-sm text-[#5a5a5a]">{p.v}</p>
              </div>
            ))}

            <div className="p-6 flex items-center gap-6">
              <a href="#" className="font-mono text-[11px] text-[#2196f3] tracking-wider hover:underline">
                READ THE DOCS →
              </a>
              <a href="#" className="font-mono text-[11px] text-[#5a5a5a] tracking-wider hover:text-[#f2ede6] transition-colors">
                GITHUB ↗
              </a>
            </div>
          </div>

          {/* Right — code block */}
          <div
            className={`flex flex-col transition-all duration-600 delay-200 ${
              vis ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
            }`}
          >
            {/* Tabs */}
            <div className="flex border-b border-[#1e1e1e]">
              {TABS.map((t, i) => (
                <button
                  key={t.label}
                  onClick={() => setTab(i)}
                  className={`flex-1 py-3 font-mono text-[10px] tracking-[0.15em] transition-colors relative ${
                    tab === i
                      ? "text-[#2196f3] bg-[#0e0e0e]"
                      : "text-[#3a3a3a] hover:text-[#5a5a5a] hover:bg-[#0a0a0a]"
                  }`}
                >
                  {t.label}
                  {tab === i && (
                    <span className="absolute bottom-0 left-0 right-0 h-px bg-[#2196f3]" />
                  )}
                </button>
              ))}
              <button
                onClick={copy}
                className="px-4 border-l border-[#1e1e1e] text-[#3a3a3a] hover:text-[#2196f3] transition-colors"
                aria-label="Copy"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-[#22c55e]" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>

            {/* Code lines */}
            <div className="flex-1 bg-[#050505] p-6 font-mono text-[12px] min-h-[300px]">
              <pre>
                {TABS[tab].code.split("\n").map((line, li) => (
                  <div
                    key={`${tab}-${li}`}
                    className="leading-7 flex gap-4"
                    style={{ animation: `fade-up 0.25s ease ${li * 45}ms both` }}
                  >
                    <span className="text-[#2e2e2e] select-none w-4 text-right shrink-0">{li + 1}</span>
                    <span className="text-[#5a5a5a]">{line}</span>
                  </div>
                ))}
              </pre>
            </div>

            {/* Footer */}
            <div className="border-t border-[#1e1e1e] px-6 py-3 flex items-center justify-between bg-[#080808]">
              <span className="font-mono text-[10px] text-[#3a3a3a]">@jarvis/sdk · v4.0.0 · stable</span>
              <div className="flex items-center gap-2">
                <span className="status-pulse w-1.5 h-1.5 rounded-full bg-[#22c55e] inline-block" />
                <span className="font-mono text-[10px] text-[#22c55e]">STABLE</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
