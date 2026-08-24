import type { TelemetryEvent } from '../api';
import { Shield, ShieldAlert, ShieldBan, ShieldCheck, Activity, SlidersHorizontal, Lock } from 'lucide-react';
import clsx from 'clsx';
import { RiskTimeline } from './RiskTimeline';

interface SecurityPanelProps {
  telemetry: TelemetryEvent | null;
  history: TelemetryEvent[];
}

export function SecurityPanel({ telemetry, history }: SecurityPanelProps) {
  if (!telemetry) {
    return (
      <div className="h-full bg-slate-900 text-slate-400 flex flex-col items-center justify-center p-8 animate-in fade-in duration-500">
        <div className="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 shadow-inner ring-1 ring-slate-700/50">
          <Shield className="w-10 h-10 text-slate-600" />
        </div>
        <h3 className="text-lg font-semibold text-slate-300 mb-2">Telemetry Standby</h3>
        <p className="text-center text-sm max-w-xs leading-relaxed">
          Behavioral metrics, risk analysis, and adaptive policy states will populate here automatically upon query submission.
        </p>
      </div>
    );
  }

  const { instantaneous_risk, smoothed_risk, signals, policy, blocked_by_policy, intent, retrieval_strategy, result_count } = telemetry;
  
  const riskLevel = policy?.risk_level || (smoothed_risk > 0.7 ? 'HIGH' : smoothed_risk > 0.25 ? 'MEDIUM' : 'LOW');
  
  const getRiskColor = (level: string) => {
    switch(level) {
      case 'LOW': return 'text-emerald-400';
      case 'MEDIUM': return 'text-amber-400';
      case 'HIGH': return 'text-red-500';
      default: return 'text-slate-400';
    }
  };

  const getRiskBg = (level: string) => {
    switch(level) {
      case 'LOW': return 'bg-emerald-500/10 border-emerald-500/20';
      case 'MEDIUM': return 'bg-amber-500/10 border-amber-500/20';
      case 'HIGH': return 'bg-red-500/10 border-red-500/20';
      default: return 'bg-slate-800 border-slate-700';
    }
  };

  const getRiskIcon = (level: string) => {
    switch(level) {
      case 'LOW': return <ShieldCheck className="w-6 h-6 text-emerald-400" />;
      case 'MEDIUM': return <ShieldAlert className="w-6 h-6 text-amber-400" />;
      case 'HIGH': return <ShieldBan className="w-6 h-6 text-red-500" />;
      default: return <Shield className="w-6 h-6 text-slate-400" />;
    }
  };

  return (
    <div className="h-full bg-slate-900 text-slate-200 overflow-y-auto custom-scrollbar">
      
      {/* Header Status */}
      <div className="p-6 border-b border-slate-800/80 bg-slate-900/50 sticky top-0 z-10 backdrop-blur-md">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-500" />
            <h2 className="text-lg font-bold tracking-tight text-white">Live Telemetry</h2>
          </div>
          <span className="text-[10px] text-slate-500 font-mono bg-slate-800 px-2 py-1 rounded border border-slate-700">
            ID: {telemetry.session_id.split('-')[0]}
          </span>
        </div>

        {/* 1. Current Risk State - High Visibility Hero Card */}
        <div className={clsx("flex items-center justify-between p-4 rounded-xl border shadow-lg transition-colors", getRiskBg(riskLevel))}>
          <div className="flex items-center space-x-4">
            <div className="bg-slate-900/50 p-2 rounded-lg ring-1 ring-white/10">
              {getRiskIcon(riskLevel)}
            </div>
            <div>
              <div className="text-xs text-slate-400 uppercase tracking-widest font-bold mb-1">System Risk Level</div>
              <div className={clsx("text-2xl font-black tracking-tight leading-none", getRiskColor(riskLevel))}>
                {riskLevel}
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-1">EWMA Score</div>
            <div className="text-xl font-mono text-white leading-none">{smoothed_risk.toFixed(3)}</div>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-8">
        
        {/* 2. Adaptive Policy (Actionable constraint block) */}
        <section>
          <div className="flex items-center space-x-2 mb-4">
            <Lock className="w-4 h-4 text-slate-400" />
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Policy Enforcement</h3>
          </div>
          
          <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 overflow-hidden">
            {blocked_by_policy ? (
              <div className="bg-red-500/10 border-b border-red-500/20 text-red-400 p-4 text-sm font-semibold flex items-center justify-center">
                <ShieldBan className="w-4 h-4 mr-2" />
                RETRIEVAL BLOCKED BY POLICY
              </div>
            ) : (
              <div className="bg-emerald-500/10 border-b border-emerald-500/20 text-emerald-400 p-4 text-sm font-semibold flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 mr-2" />
                RETRIEVAL PERMITTED
              </div>
            )}
            
            <div className="grid grid-cols-3 divide-x divide-slate-700/50">
              <div className="p-4 text-center">
                <div className="text-2xl font-mono font-medium text-white mb-1">
                  {policy?.attenuation_factor?.toFixed(2) || '1.00'}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Attenuation</div>
              </div>
              <div className="p-4 text-center">
                <div className="text-2xl font-mono font-medium text-white mb-1">
                  {policy?.effective_context_limit ?? 20}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Max Records</div>
              </div>
              <div className="p-4 text-center">
                <div className="text-2xl font-mono font-medium text-white mb-1">
                  {policy?.effective_graph_depth ?? 5}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Max Depth</div>
              </div>
            </div>
            <div className="bg-slate-900/50 p-3 border-t border-slate-700/50 flex justify-between text-[11px] font-mono text-slate-400">
              <span>Intent: {intent}</span>
              <span>Strategy: {retrieval_strategy}</span>
              <span>Records Found: {result_count}</span>
            </div>
          </div>
        </section>

        {/* 3. Risk Progression Timeline */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-slate-400" />
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Risk Timeline</h3>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">queries: {history.length}</span>
          </div>
          <div className="bg-slate-800/30 rounded-xl border border-slate-700/50 p-4 pt-6">
            <RiskTimeline history={history} />
          </div>
        </section>

        {/* 4. Behavioral Signals */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <SlidersHorizontal className="w-4 h-4 text-slate-400" />
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Behavioral Signals</h3>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Inst. Risk: {instantaneous_risk.toFixed(3)}</span>
          </div>
          
          <div className="space-y-5 bg-slate-800/30 rounded-xl border border-slate-700/50 p-5">
            {[
              { label: "Semantic Drift", symbol: "S_sem", value: signals.semantic_drift, color: "bg-blue-500" },
              { label: "Temporal Frequency", symbol: "S_temp", value: signals.temporal_frequency, color: "bg-indigo-500" },
              { label: "Entity Focus", symbol: "S_ent", value: signals.entity_focus, color: "bg-purple-500" },
              { label: "Graph Footprint", symbol: "S_graph", value: signals.graph_footprint, color: "bg-emerald-500" },
            ].map((sig) => (
              <div key={sig.symbol}>
                <div className="flex justify-between items-end mb-2">
                  <div>
                    <span className="text-sm font-medium text-slate-200">{sig.label}</span>
                    <span className="ml-2 text-[10px] text-slate-500 font-mono uppercase">({sig.symbol})</span>
                  </div>
                  <span className="text-xs font-mono text-slate-400">{sig.value.toFixed(3)}</span>
                </div>
                <div className="h-1.5 w-full bg-slate-700 rounded-full overflow-hidden shadow-inner">
                  <div 
                    className={clsx("h-full rounded-full transition-all duration-500", sig.color)} 
                    style={{ width: `${Math.min(sig.value * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
}
