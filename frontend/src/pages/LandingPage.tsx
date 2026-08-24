import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Activity, Lock, Database, Network, Server, ArrowRight, BrainCircuit } from 'lucide-react';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-200">
      
      {/* 1. Header Navigation */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200 h-16 flex items-center justify-between px-6 lg:px-12">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center shadow-sm">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900 leading-none">AegisGraph</h1>
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Graph-RAG Security Framework</span>
          </div>
        </div>
        <button 
          onClick={() => navigate('/app')}
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center shadow-sm"
        >
          Launch AegisGraph
          <ArrowRight className="w-4 h-4 ml-2" />
        </button>
      </header>

      <main>
        {/* 2. Hero Section */}
        <section className="pt-24 pb-16 px-6 lg:px-12 text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium mb-8 border border-blue-100">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-600"></span>
            </span>
            <span>Prototype v0.6 Available</span>
          </div>
          <h2 className="text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 mb-6 leading-tight">
            Secure your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Graph-RAG</span> intelligence.
          </h2>
          <p className="text-lg lg:text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            AegisGraph is a behavioral threat detection and adaptive response framework for Graph-RAG knowledge systems. Stop reconnaissance and data exfiltration before the LLM generates a response.
          </p>
          <button 
            onClick={() => navigate('/app')}
            className="bg-slate-900 hover:bg-slate-800 text-white px-8 py-3.5 rounded-lg text-lg font-semibold transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 flex items-center mx-auto"
          >
            Launch Demonstration
            <ArrowRight className="w-5 h-5 ml-2" />
          </button>
        </section>

        {/* 3. Problem / Value Proposition */}
        <section className="py-16 bg-white border-y border-slate-100">
          <div className="max-w-5xl mx-auto px-6 lg:px-12 flex flex-col md:flex-row items-center gap-12">
            <div className="flex-1">
              <h3 className="text-3xl font-bold mb-4 text-slate-900">The Graph Retrieval Vulnerability</h3>
              <p className="text-slate-600 text-lg leading-relaxed">
                Graph-based retrieval systems (Graph-RAG) excel at uncovering hidden connections. However, this same capability can expose sensitive organizational relationships through repeated, structured probing. Standard semantic filters fail to detect this escalating intent.
              </p>
            </div>
            <div className="flex-1 bg-slate-50 p-6 rounded-xl border border-slate-200">
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-red-100 rounded-lg shrink-0">
                  <Lock className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 mb-1">Standard RAG Fails</h4>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    Without behavioral memory, an attacker can map your entire knowledge graph one benign-looking query at a time.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 4. Core Capabilities */}
        <section className="py-20 px-6 lg:px-12 max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-slate-900">Core Capabilities</h3>
            <p className="text-slate-500 mt-4 max-w-2xl mx-auto">AegisGraph introduces a continuous security layer that monitors session context and enforces adaptive constraints dynamically.</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
              <Activity className="w-10 h-10 text-blue-600 mb-4" />
              <h4 className="text-lg font-semibold mb-2">Behavioral Risk Analysis</h4>
              <p className="text-sm text-slate-600 leading-relaxed">Calculates real-time EWMA risk by tracking semantic drift, temporal frequency, entity focus, and graph footprint across user sessions.</p>
            </div>
            
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
              <ShieldCheck className="w-10 h-10 text-indigo-600 mb-4" />
              <h4 className="text-lg font-semibold mb-2">Adaptive Policy Enforcement</h4>
              <p className="text-sm text-slate-600 leading-relaxed">Dynamically generates a security policy (attentuation, context limits, graph depth) proportional to the user's compounded behavioral risk.</p>
            </div>
            
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
              <Network className="w-10 h-10 text-emerald-600 mb-4" />
              <h4 className="text-lg font-semibold mb-2">Controlled Graph Retrieval</h4>
              <p className="text-sm text-slate-600 leading-relaxed">Retrieval strategies are mathematically constrained by the Adaptive Policy before interacting with the Neo4j knowledge graph.</p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
              <Server className="w-10 h-10 text-purple-600 mb-4" />
              <h4 className="text-lg font-semibold mb-2">Real-Time Telemetry</h4>
              <p className="text-sm text-slate-600 leading-relaxed">Provides developers with instant, passive visualization of instantaneous risk and policy boundaries via the frontend dashboard.</p>
            </div>
          </div>
        </section>

        {/* 5. Architecture Flow */}
        <section className="py-20 bg-slate-900 text-white border-t border-slate-800">
          <div className="max-w-5xl mx-auto px-6 lg:px-12">
            <div className="text-center mb-16">
              <h3 className="text-3xl font-bold">Secure Architecture</h3>
              <p className="text-slate-400 mt-4 max-w-2xl mx-auto">Security enforcement occurs critically before the context reaches the local LLM, preventing data exposure at the source.</p>
            </div>

            <div className="flex flex-col lg:flex-row items-center justify-between gap-4 font-mono text-sm">
              <div className="flex-1 bg-slate-800 p-4 rounded-lg border border-slate-700 text-center w-full lg:w-auto">
                <span className="text-blue-400 font-semibold block mb-1">Step 1</span>
                User Query
              </div>
              <ArrowRight className="w-6 h-6 text-slate-600 hidden lg:block rotate-90 lg:rotate-0" />
              
              <div className="flex-1 bg-slate-800 p-4 rounded-lg border border-blue-900/50 text-center w-full lg:w-auto ring-1 ring-blue-500/30">
                <span className="text-blue-400 font-semibold block mb-1">Step 2</span>
                Behavioral Analysis & Risk Assessment
              </div>
              <ArrowRight className="w-6 h-6 text-slate-600 hidden lg:block rotate-90 lg:rotate-0" />
              
              <div className="flex-1 bg-slate-800 p-4 rounded-lg border border-indigo-900/50 text-center w-full lg:w-auto ring-1 ring-indigo-500/30">
                <span className="text-indigo-400 font-semibold block mb-1">Step 3</span>
                Adaptive Policy Applied
              </div>
              <ArrowRight className="w-6 h-6 text-slate-600 hidden lg:block rotate-90 lg:rotate-0" />
              
              <div className="flex-1 bg-slate-800 p-4 rounded-lg border border-emerald-900/50 text-center w-full lg:w-auto ring-1 ring-emerald-500/30">
                <span className="text-emerald-400 font-semibold block mb-1">Step 4</span>
                <Database className="w-4 h-4 inline-block mr-1 mb-0.5" />
                Controlled Retrieval
              </div>
              <ArrowRight className="w-6 h-6 text-slate-600 hidden lg:block rotate-90 lg:rotate-0" />

              <div className="flex-1 bg-slate-800 p-4 rounded-lg border border-slate-700 text-center w-full lg:w-auto">
                <span className="text-blue-400 font-semibold block mb-1">Step 5</span>
                <BrainCircuit className="w-4 h-4 inline-block mr-1 mb-0.5" />
                Local LLM Response
              </div>
            </div>
          </div>
        </section>

        {/* 6. Final CTA */}
        <section className="py-24 px-6 lg:px-12 text-center bg-white">
          <h3 className="text-3xl font-bold text-slate-900 mb-6">Ready to see it in action?</h3>
          <p className="text-slate-600 max-w-xl mx-auto mb-10">
            Experience the real-time behavioral monitoring and adaptive graph policy enforcement firsthand.
          </p>
          <button 
            onClick={() => navigate('/app')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3.5 rounded-lg text-lg font-semibold transition-colors shadow-lg hover:shadow-xl inline-flex items-center"
          >
            Launch Dashboard
            <ArrowRight className="w-5 h-5 ml-2" />
          </button>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-50 py-8 text-center text-slate-500 text-sm border-t border-slate-200">
        <p>AegisGraph Prototype Phase 9. Developed for secure Graph-RAG research.</p>
      </footer>
    </div>
  );
}
