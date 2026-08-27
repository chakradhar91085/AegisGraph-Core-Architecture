"use client";

import { useEffect, useState } from "react";

const LINKS = {
  PLATFORM: [
    { name: "Agents",          href: "#features" },
    { name: "Orchestration",   href: "#how-it-works" },
    { name: "Infrastructure",  href: "#infrastructure" },
    { name: "Integrations",    href: "#integrations" },
    { name: "Security",        href: "#security" },
  ],
  DEVELOPERS: [
    { name: "Documentation",   href: "#developers" },
    { name: "API Reference",   href: "#" },
    { name: "SDK",             href: "#developers" },
    { name: "Status",          href: "#" },
    { name: "Changelog",       href: "#" },
  ],
  COMPANY: [
    { name: "About",           href: "#" },
    { name: "Blog",            href: "#" },
    { name: "Careers",         href: "#", badge: "HIRING" },
    { name: "Contact",         href: "#" },
  ],
  LEGAL: [
    { name: "Privacy",         href: "#" },
    { name: "Terms",           href: "#" },
    { name: "Security",        href: "#security" },
  ],
};

export function FooterSection() {
  const [time, setTime] = useState("");

  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString("en-US", { hour12: false }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <footer className="border-t border-[#1e1e1e] bg-[#050505] pt-20 pb-10">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-12 lg:gap-8 mb-20">
          
          <div className="col-span-2">
            <div className="flex items-center gap-3 mb-6">
              <div className="relative flex items-center justify-center w-6 h-6 text-[#2196f3]">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round" className="w-full h-full drop-shadow-[0_0_8px_rgba(33,150,243,0.2)]">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <circle cx="12" cy="9" r="1.5" fill="currentColor" />
                  <circle cx="8.5" cy="14" r="1.5" fill="currentColor" />
                  <circle cx="15.5" cy="14" r="1.5" fill="currentColor" />
                  <path d="M12 9l-3.5 5M12 9l3.5 5M8.5 14h7" strokeWidth="1" strokeDasharray="1 2" opacity="0.8" />
                </svg>
              </div>
              <span className="font-display text-xl tracking-[0.2em] text-[#f2ede6] font-bold italic">AEGISGRAPH</span>
            </div>
            <p className="text-[#5a5a5a] text-sm leading-relaxed max-w-sm mb-8 font-mono">
              The behavioral security layer to secure, monitor, and protect enterprise Graph-RAG workflows in production.
            </p>
            <div className="flex gap-5 mt-6">
              {["TWITTER", "GITHUB", "DISCORD"].map(s => (
                <a key={s} href="#" className="font-mono text-[10px] tracking-widest text-[#3a3a3a] hover:text-[#2196f3] transition-colors">
                  {s} ↗
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {Object.entries(LINKS).map(([section, links]) => (
              <div key={section}>
                <h3 className="font-mono text-[9px] tracking-[0.2em] text-[#2196f3] mb-5">{section}</h3>
                <ul className="space-y-3">
                  {links.map(l => (
                    <li key={l.name}>
                      <a href={l.href} className="font-mono text-[11px] text-[#3a3a3a] hover:text-[#f2ede6] transition-colors inline-flex items-center gap-2">
                        {l.name}
                        {"badge" in l && l.badge && (
                          <span className="text-[9px] border border-[#2196f3]/30 text-[#2196f3] px-1.5 py-0.5 tracking-wider">
                            {l.badge}
                          </span>
                        )}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom bar */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="font-mono text-[10px] text-[#3a3a3a] uppercase">
            © 2025 AEGISGRAPH INC. ALL RIGHTS RESERVED.
          </span>
          <div className="flex items-center gap-6">
            <span className="font-mono text-[10px] text-[#3a3a3a] tabular-nums">{time} UTC</span>
            <div className="flex items-center gap-2">
              <span className="status-pulse w-1.5 h-1.5 rounded-full bg-[#22c55e] inline-block" />
              <span className="font-mono text-[10px] text-[#22c55e] tracking-widest">ALL_SYSTEMS_OPERATIONAL</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
