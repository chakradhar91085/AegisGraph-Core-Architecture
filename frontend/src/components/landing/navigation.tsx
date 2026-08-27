"use client";

import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";

const navLinks = [
  { name: "PRODUCT",      href: "#product" },
  { name: "ARCHITECTURE", href: "#architecture" },
  { name: "SECURITY",     href: "#security" },
  { name: "RESEARCH",     href: "#research" },
];

export function Navigation() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [time, setTime] = useState("");

  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString("en-US", { hour12: false }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled ? "bg-[#050505]/95 backdrop-blur-sm border-b border-[#1e1e1e]" : "bg-transparent"
        }`}
      >
        {/* Top status bar */}
        <div className="border-b border-[#1e1e1e] px-6 lg:px-12 h-8 flex items-center justify-between">
          <span className="font-mono text-[10px] text-[#3a3a3a] tracking-widest uppercase">
            SYS:AEGISGRAPH &nbsp;/&nbsp; BUILD 2026.08
          </span>
          <div className="hidden md:flex items-center gap-6">
            <span className="font-mono text-[10px] text-[#3a3a3a]">
              <span className="text-[#22c55e]">●</span>&nbsp;ALL_SYSTEMS_NOMINAL
            </span>
            <span className="font-mono text-[10px] text-[#3a3a3a] tabular-nums">{time} UTC</span>
          </div>
        </div>

        {/* Main nav */}
        <div className="px-6 lg:px-12 h-14 flex items-center justify-between">
          {/* Logo */}
          <a href="#" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-7 h-7 text-[#2196f3] group-hover:text-[#42a5f5] transition-all duration-300">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round" className="w-full h-full drop-shadow-[0_0_8px_rgba(33,150,243,0.2)] group-hover:drop-shadow-[0_0_12px_rgba(66,165,245,0.4)]">
                {/* Minimal shield outline */}
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                {/* Graph nodes inside */}
                <circle cx="12" cy="9" r="1.5" fill="currentColor" />
                <circle cx="8.5" cy="14" r="1.5" fill="currentColor" />
                <circle cx="15.5" cy="14" r="1.5" fill="currentColor" />
                {/* Graph edges */}
                <path d="M12 9l-3.5 5M12 9l3.5 5M8.5 14h7" strokeWidth="1" strokeDasharray="1 2" opacity="0.8" />
              </svg>
            </div>
            <span className="font-display text-2xl tracking-[0.15em] text-[#f2ede6]">AEGISGRAPH</span>
            <span className="hidden lg:block font-mono text-[10px] text-[#3a3a3a] border-l border-[#1e1e1e] pl-3 ml-1 tracking-widest">
              BEHAVIORAL SECURITY
            </span>
          </a>

          {/* Desktop links */}
          <nav className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="font-mono text-[11px] tracking-[0.18em] text-[#5a5a5a] hover:text-[#2196f3] hover:drop-shadow-[0_0_8px_rgba(33,150,243,0.3)] transition-all duration-300"
              >
                {link.name}
              </a>
            ))}
          </nav>

          {/* CTA */}
          <div className="hidden md:flex items-center gap-4">
            <SignedOut>
              <SignInButton mode="modal" forceRedirectUrl="/app">
                <button className="font-mono text-[11px] tracking-widest text-[#5a5a5a] hover:text-[#f2ede6] transition-colors duration-300 cursor-pointer">
                  SIGN IN
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <a
                href="/app"
                className="font-mono text-[11px] tracking-widest bg-[#2196f3] text-[#050505] px-5 h-9 flex items-center hover:bg-[#42a5f5] hover:shadow-[0_0_15px_rgba(33,150,243,0.4)] hover:-translate-y-[1px] transition-all duration-300 font-semibold mr-2"
              >
                LAUNCH AEGISGRAPH →
              </a>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>

          {/* Mobile burger */}
          <button
            onClick={() => setOpen(!open)}
            className="md:hidden text-[#f2ede6] p-1"
            aria-label="Toggle menu"
          >
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </header>

      {/* Mobile menu */}
      <div
        className={`fixed inset-0 z-40 bg-[#050505] flex flex-col transition-opacity duration-300 ${
          open ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
        style={{ paddingTop: "88px" }}
      >
        <div className="border-t border-[#1e1e1e] flex flex-col">
          {navLinks.map((link, i) => (
            <a
              key={link.name}
              href={link.href}
              onClick={() => setOpen(false)}
              className={`border-b border-[#1e1e1e] px-8 py-7 font-display text-5xl tracking-wider text-[#f2ede6] hover:text-[#2196f3] transition-all duration-300 flex items-center justify-between ${
                open ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-4"
              }`}
              style={{ transitionDelay: open ? `${i * 60}ms` : "0ms" }}
            >
              {link.name}
              <span className="font-mono text-xs text-[#3a3a3a]">
                {String(i + 1).padStart(2, "0")}
              </span>
            </a>
          ))}
        </div>
        <div className="mt-auto p-8 border-t border-[#1e1e1e]">
          <a
            href="/app"
            onClick={() => setOpen(false)}
            className="w-full block text-center font-mono text-sm tracking-widest bg-[#2196f3] text-[#050505] py-5 font-semibold"
          >
            LAUNCH AEGISGRAPH →
          </a>
        </div>
      </div>
    </>
  );
}
