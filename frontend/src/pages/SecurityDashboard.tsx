import { useChat } from '../contexts/ChatContext';
import { SecurityPanel } from '../components/SecurityPanel';
import type { TelemetryEvent } from '../api';

export function SecurityDashboard() {
  const { messages } = useChat();
  
  // Extract telemetry history from agent messages
  const telemetryHistory = messages
    .filter(m => m.sender === 'agent' && m.telemetry)
    .map(m => m.telemetry!) as TelemetryEvent[];
  
  const currentTelemetry = telemetryHistory.length > 0 
    ? telemetryHistory[telemetryHistory.length - 1] 
    : null;

  return (
    <div className="flex flex-col h-full bg-[#050505] p-6 w-full mx-auto relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-[#2196f3] opacity-[0.02] blur-[120px] pointer-events-none rounded-full" />
      
      {/* Header */}
      <div className="mb-6 flex items-end justify-between z-10 shrink-0">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-display font-bold text-[#f2ede6] uppercase tracking-wide">Security Dashboard</h1>
            <div className="sys-tag">Telemetry</div>
          </div>
          <p className="text-sm text-[#8a8a8a] font-mono tracking-tight">
            AEGISGRAPH // LIVE BEHAVIORAL RISK ANALYSIS
          </p>
        </div>
      </div>
      
      <div className="flex-1 min-h-0 bg-[#0a0a0a] border border-[#1e1e1e] shadow-2xl flex flex-col relative z-10 overflow-hidden">
        {telemetryHistory.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-[#5a5a5a]">
            <div className="w-16 h-16 mb-4 rounded-sm border border-[#1e1e1e] bg-[#0e0e0e] flex items-center justify-center">
              <svg className="w-8 h-8 text-[#2196f3] opacity-50" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <circle cx="12" cy="9" r="1.5" />
                <circle cx="8.5" cy="14" r="1.5" />
                <circle cx="15.5" cy="14" r="1.5" />
              </svg>
            </div>
            <p className="text-sm font-display uppercase tracking-widest text-[#8a8a8a] mb-1">Awaiting Telemetry</p>
            <p className="text-xs font-mono max-w-sm text-center">Execute a query in the Secure Workspace to generate behavioral security signals and risk assessments.</p>
          </div>
        ) : (
          <div className="h-full flex flex-col">
            <SecurityPanel telemetry={currentTelemetry} history={telemetryHistory} />
          </div>
        )}
      </div>
    </div>
  );
}
