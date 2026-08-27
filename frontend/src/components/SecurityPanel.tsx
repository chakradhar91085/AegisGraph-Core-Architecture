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
      <div className="h-full bg-[#0a0a0a] text-[#8a8a8a] flex flex-col items-center justify-center p-8 animate-in fade-in duration-500">
        <div className="w-20 h-20 bg-[#0e0e0e] rounded-sm flex items-center justify-center mb-6 border border-[#1e1e1e]">
          <Shield className="w-10 h-10 text-[#5a5a5a]" />
        </div>
        <h3 className="text-sm font-display uppercase tracking-widest text-[#f2ede6] mb-2">Telemetry Standby</h3>
        <p className="text-center text-xs font-mono max-w-xs leading-relaxed">
          Behavioral metrics, risk analysis, and adaptive policy states will populate here automatically upon query submission.
        </p>
      </div>
    );
  }

  const { instantaneous_risk, smoothed_risk, signals, policy, blocked_by_policy, intent, retrieval_strategy, result_count } = telemetry;
  
  const riskLevel = policy?.risk_level || (smoothed_risk > 0.7 ? 'HIGH' : smoothed_risk > 0.25 ? 'MEDIUM' : 'LOW');
  
  const getRiskColor = (level: string) => {
    switch(level) {
      case 'LOW': return 'text-green-500';
      case 'MEDIUM': return 'text-amber-500';
      case 'HIGH': 
      case 'CRITICAL': return 'text-red-500';
      default: return 'text-[#8a8a8a]';
    }
  };

  const getRiskBg = (level: string) => {
    switch(level) {
      case 'LOW': return 'bg-green-950/20 border-green-900/30';
      case 'MEDIUM': return 'bg-amber-950/20 border-amber-900/30';
      case 'HIGH':
      case 'CRITICAL': return 'bg-red-950/20 border-red-900/30';
      default: return 'bg-[#0e0e0e] border-[#1e1e1e]';
    }
  };

  const getRiskIcon = (level: string) => {
    switch(level) {
      case 'LOW': return <ShieldCheck className="w-6 h-6 text-green-500" />;
      case 'MEDIUM': return <ShieldAlert className="w-6 h-6 text-amber-500" />;
      case 'HIGH':
      case 'CRITICAL': return <ShieldBan className="w-6 h-6 text-red-500" />;
      default: return <Shield className="w-6 h-6 text-[#5a5a5a]" />;
    }
  };

  return (
    <div className="h-full bg-[#0a0a0a] text-[#f2ede6] overflow-y-auto custom-scrollbar">
      
      {/* Header Status */}
      <div className="p-6 border-b border-[#1e1e1e] bg-[#050505]/90 sticky top-0 z-10 backdrop-blur-md">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-[#2196f3]" />
            <h2 className="text-sm font-display font-bold tracking-widest uppercase text-[#f2ede6]">Live Telemetry</h2>
          </div>
          <span className="text-[10px] text-[#5a5a5a] font-mono uppercase tracking-widest bg-[#0e0e0e] px-2 py-1 border border-[#1e1e1e]">
            ID: {telemetry.session_id.split('-')[0]}
          </span>
        </div>

        {/* 1. Current Risk State - High Visibility Hero Card */}
        <div className={clsx("flex items-center justify-between p-4 border transition-colors", getRiskBg(riskLevel))}>
          <div className="flex items-center space-x-4">
            <div className="bg-[#050505] p-2 border border-[#1e1e1e]">
              {getRiskIcon(riskLevel)}
            </div>
            <div>
              <div className="text-[10px] text-[#5a5a5a] uppercase font-mono tracking-widest mb-1">System Risk Level</div>
              <div className={clsx("text-2xl font-display font-bold tracking-widest uppercase leading-none", getRiskColor(riskLevel))}>
                {riskLevel}
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-[#5a5a5a] uppercase font-mono tracking-widest mb-1">EWMA Score</div>
            <div className="text-xl font-mono text-[#f2ede6] leading-none">{smoothed_risk.toFixed(3)}</div>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-8">
        
        {/* 2. Adaptive Policy (Actionable constraint block) */}
        <section>
          <div className="flex items-center space-x-2 mb-4">
            <Lock className="w-3 h-3 text-[#5a5a5a]" />
            <h3 className="text-[10px] font-mono font-bold uppercase tracking-widest text-[#8a8a8a]">Policy Enforcement</h3>
          </div>
          
          <div className="bg-[#0e0e0e] border border-[#1e1e1e] overflow-hidden">
            {blocked_by_policy ? (
              <div className="bg-red-950/30 border-b border-red-900/50 text-red-500 p-3 text-[11px] font-mono uppercase tracking-widest flex items-center justify-center">
                <ShieldBan className="w-4 h-4 mr-2" />
                RETRIEVAL BLOCKED BY POLICY
              </div>
            ) : (
              <div className="bg-green-950/30 border-b border-green-900/50 text-green-500 p-3 text-[11px] font-mono uppercase tracking-widest flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 mr-2" />
                RETRIEVAL PERMITTED
              </div>
            )}
            
            <div className="grid grid-cols-3 divide-x divide-[#1e1e1e]">
              <div className="p-4 text-center">
                <div className="text-xl font-mono text-[#f2ede6] mb-1">
                  {policy?.attenuation_factor?.toFixed(2) || '1.00'}
                </div>
                <div className="text-[10px] text-[#5a5a5a] font-mono uppercase tracking-widest">Attenuation</div>
              </div>
              <div className="p-4 text-center">
                <div className="text-xl font-mono text-[#f2ede6] mb-1">
                  {policy?.effective_context_limit ?? 20}
                </div>
                <div className="text-[10px] text-[#5a5a5a] font-mono uppercase tracking-widest">Max Records</div>
              </div>
              <div className="p-4 text-center">
                <div className="text-xl font-mono text-[#f2ede6] mb-1">
                  {policy?.effective_graph_depth ?? 5}
                </div>
                <div className="text-[10px] text-[#5a5a5a] font-mono uppercase tracking-widest">Max Depth</div>
              </div>
            </div>
            <div className="bg-[#050505] p-3 border-t border-[#1e1e1e] flex justify-between text-[10px] font-mono uppercase tracking-wider text-[#5a5a5a]">
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
              <Activity className="w-3 h-3 text-[#5a5a5a]" />
              <h3 className="text-[10px] font-mono font-bold uppercase tracking-widest text-[#8a8a8a]">Risk Timeline</h3>
            </div>
            <span className="text-[10px] text-[#5a5a5a] font-mono uppercase tracking-widest">queries: {history.length}</span>
          </div>
          <div className="bg-[#0e0e0e] border border-[#1e1e1e] p-4 pt-6">
            <RiskTimeline history={history} />
          </div>
        </section>

        {/* 4. Behavioral Signals */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <SlidersHorizontal className="w-3 h-3 text-[#5a5a5a]" />
              <h3 className="text-[10px] font-mono font-bold uppercase tracking-widest text-[#8a8a8a]">Behavioral Signals</h3>
            </div>
            <span className="text-[10px] text-[#5a5a5a] font-mono uppercase tracking-widest">Inst. Risk: {instantaneous_risk.toFixed(3)}</span>
          </div>
          
          <div className="space-y-5 bg-[#0e0e0e] border border-[#1e1e1e] p-5">
            {[
              { label: "Semantic Drift", symbol: "S_sem", value: signals.semantic_drift, color: "bg-[#2196f3]" },
              { label: "Temporal Frequency", symbol: "S_temp", value: signals.temporal_frequency, color: "bg-[#2196f3]" },
              { label: "Entity Focus", symbol: "S_ent", value: signals.entity_focus, color: "bg-[#2196f3]" },
              { label: "Graph Footprint", symbol: "S_graph", value: signals.graph_footprint, color: "bg-[#2196f3]" },
            ].map((sig) => (
              <div key={sig.symbol}>
                <div className="flex justify-between items-end mb-2">
                  <div>
                    <span className="text-xs font-medium text-[#f2ede6]">{sig.label}</span>
                    <span className="ml-2 text-[10px] text-[#5a5a5a] font-mono uppercase">({sig.symbol})</span>
                  </div>
                  <span className="text-xs font-mono text-[#8a8a8a]">{sig.value.toFixed(3)}</span>
                </div>
                <div className="h-1 w-full bg-[#141414] overflow-hidden">
                  <div 
                    className={clsx("h-full transition-all duration-500", sig.color)} 
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
