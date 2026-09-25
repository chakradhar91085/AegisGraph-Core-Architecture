import { SignedIn, SignedOut, SignInButton } from "@clerk/clerk-react";
import { ArrowDown, ShieldCheck } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative min-h-[85vh] flex flex-col justify-center overflow-x-hidden pt-[88px] bg-slate-950" id="overview">
      <div className="relative z-20 max-w-[1400px] mx-auto px-6 lg:px-12 py-20 lg:py-28 w-full">
        
        <div className="grid lg:grid-cols-2 gap-16 lg:gap-24 items-center">
          
          {/* LEFT COLUMN: Text */}
          <div className="relative z-10 lg:pr-8">
            <div className="mb-6 inline-flex items-center gap-2 border border-blue-900/50 bg-blue-950/30 px-3 py-1.5 rounded-sm">
              <ShieldCheck className="w-4 h-4 text-blue-400" />
              <p className="font-mono text-xs tracking-widest text-blue-400 font-semibold">
                BEHAVIORAL SECURITY FOR GRAPH-RAG
              </p>
            </div>

            <h1 className="font-sans font-semibold text-5xl sm:text-6xl lg:text-[64px] leading-[1.1] tracking-tight text-slate-50 mb-6">
              SECURE HOW AI EXPLORES KNOWLEDGE.
            </h1>
            
            <p className="text-base sm:text-lg text-slate-400 leading-relaxed max-w-xl mb-10 font-sans">
              AegisGraph is a behavioral security framework for Retrieval-Augmented Generation systems that monitors user interaction patterns and dynamically controls information exposure during graph-based retrieval.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 w-fit">
              <SignedOut>
                <SignInButton mode="modal" forceRedirectUrl="/app">
                  <button className="inline-flex items-center justify-center gap-2 bg-blue-600 text-slate-50 font-sans text-sm px-6 py-3.5 hover:bg-blue-500 transition-colors font-semibold rounded-sm">
                    Explore AegisGraph
                  </button>
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <a
                  href="/app"
                  className="inline-flex items-center justify-center gap-2 bg-blue-600 text-slate-50 font-sans text-sm px-6 py-3.5 hover:bg-blue-500 transition-colors font-semibold rounded-sm"
                >
                  Explore AegisGraph
                </a>
              </SignedIn>
              <a
                href="#architecture"
                className="inline-flex items-center justify-center gap-2 border border-slate-700 text-slate-300 font-sans text-sm px-6 py-3.5 hover:bg-slate-800 hover:text-slate-50 transition-colors rounded-sm"
              >
                View Architecture
              </a>
            </div>
          </div>

          {/* RIGHT COLUMN: Static Pipeline */}
          <div className="relative z-10 flex justify-center lg:justify-end">
            <div className="w-full max-w-sm bg-slate-900/50 border border-slate-800 p-8 rounded-lg shadow-xl flex flex-col items-center">
              
              <PipelineStep title="User Query" />
              <Arrow />
              <PipelineStep title="Behavior Signals" highlight={true} />
              <Arrow />
              <PipelineStep title="Risk Assessment" highlight={true} />
              <Arrow />
              <PipelineStep title="Adaptive Policy" highlight={true} />
              <Arrow />
              <PipelineStep title="Controlled Graph Retrieval" />
              <Arrow />
              <PipelineStep title="Grounded Response" success={true} />
              
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}

function PipelineStep({ title, highlight = false, success = false }: { title: string, highlight?: boolean, success?: boolean }) {
  let bg = "bg-slate-950";
  let border = "border-slate-800";
  let text = "text-slate-300";

  if (highlight) {
    bg = "bg-blue-950/20";
    border = "border-blue-900/50";
    text = "text-blue-400";
  } else if (success) {
    bg = "bg-emerald-950/20";
    border = "border-emerald-900/50";
    text = "text-emerald-400";
  }

  return (
    <div className={`w-full py-3 px-4 rounded border ${bg} ${border} text-center font-mono text-sm tracking-wide ${text}`}>
      {title}
    </div>
  );
}

function Arrow() {
  return (
    <div className="py-2 text-slate-700">
      <ArrowDown className="w-4 h-4" />
    </div>
  );
}
