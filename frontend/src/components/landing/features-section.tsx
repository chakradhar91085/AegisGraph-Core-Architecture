export function FeaturesSection() {
  const signals = [
    {
      title: "Semantic Drift",
      identifier: "S_sem",
      desc: "Measures how the user's queries shift semantically over time.",
    },
    {
      title: "Temporal Frequency",
      identifier: "S_temp",
      desc: "Measures how rapidly queries are issued relative to recent activity.",
    },
    {
      title: "Entity Focus",
      identifier: "S_ent",
      desc: "Measures concentration of attention around entities using entity distribution/entropy.",
    },
    {
      title: "Graph Footprint",
      identifier: "S_graph",
      desc: "Measures the user's graph exploration footprint, such as retrieval depth/volume.",
    }
  ];

  return (
    <section className="py-24 bg-slate-950 relative border-t border-slate-900" id="features">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="font-sans font-semibold text-3xl md:text-4xl text-slate-50 mb-4 tracking-tight">
            Four Behavioral Signals
          </h2>
          <p className="text-slate-400 text-lg leading-relaxed font-sans">
            AegisGraph monitors four core telemetry streams during interactions to build a live behavioral profile.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {signals.map((signal) => (
            <div
              key={signal.identifier}
              className="bg-slate-900 border border-slate-800 p-8 rounded-lg flex flex-col"
            >
              <div className="mb-4">
                <span className="inline-block bg-slate-800 border border-slate-700 text-blue-400 font-mono text-xs px-3 py-1 rounded">
                  {signal.identifier}
                </span>
              </div>
              <h3 className="font-sans font-semibold text-lg text-slate-200 mb-3">
                {signal.title}
              </h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                {signal.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
