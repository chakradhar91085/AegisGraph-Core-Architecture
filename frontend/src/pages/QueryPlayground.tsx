import { useChat } from '../contexts/ChatContext';
import { Shield, ShieldAlert, Activity, User, Cpu } from 'lucide-react';
import { ChatPanel } from '../components/ChatPanel';

export function QueryPlayground() {
  const { messages, loading, error, role, setRole, llmProvider, setLlmProvider, sendMessage } = useChat();

  const telemetryHistory = messages
    .filter(m => m.sender === 'agent' && m.telemetry)
    .map(m => m.telemetry!);
    
  const telemetry = telemetryHistory.length > 0 ? telemetryHistory[telemetryHistory.length - 1] : null;

  const isBlocked = telemetry?.blocked_by_policy ?? false;
  const riskScore = telemetry?.smoothed_risk ?? 0;
  
  return (
    <div className="flex-1 flex flex-col h-full bg-[#050505] p-6 w-full mx-auto relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-[#2196f3] opacity-[0.03] blur-[100px] pointer-events-none rounded-full" />
      
      {/* Header */}
      <div className="mb-6 flex items-end justify-between z-10 shrink-0">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-display font-bold text-[#f2ede6] uppercase tracking-wide">Secure Workspace</h1>
            <div className="sys-tag">Intelligence</div>
          </div>
          <p className="text-sm text-[#8a8a8a] font-mono tracking-tight">
            AEGISGRAPH // KNOWLEDGE RETRIEVAL TERMINAL
          </p>
        </div>
      </div>

      {/* Security & Controls Strip */}
      <div className="mb-6 grid grid-cols-4 gap-4 z-10 shrink-0">
        
        {/* Role Selector Box */}
        <div className="bg-[#0e0e0e] border border-[#1e1e1e] p-3 flex items-center justify-between">
          <div className="flex items-center gap-3 w-full">
            <div className="w-8 h-8 rounded-sm bg-[#141414] border border-[#2e2e2e] flex items-center justify-center shrink-0">
              <User className="w-4 h-4 text-[#8a8a8a]" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-[10px] text-[#5a5a5a] font-mono uppercase mb-0.5">Current Role</div>
              <select 
                value={role}
                onChange={(e) => setRole(e.target.value as any)}
                className="w-full bg-[#141414] border border-[#2e2e2e] rounded-sm px-2 py-0.5 text-xs font-mono font-medium text-[#2196f3] outline-none cursor-pointer"
              >
                <option value="Standard" className="bg-[#0e0e0e] text-[#f2ede6]">Standard</option>
                <option value="Analyst" className="bg-[#0e0e0e] text-[#f2ede6]">Analyst</option>
                <option value="Auditor" className="bg-[#0e0e0e] text-[#f2ede6]">Auditor</option>
              </select>
            </div>
          </div>
        </div>

        {/* LLM Provider Box */}
        <div className="bg-[#0e0e0e] border border-[#1e1e1e] p-3 flex items-center justify-between">
          <div className="flex items-center gap-3 w-full">
            <div className="w-8 h-8 rounded-sm bg-[#141414] border border-[#2e2e2e] flex items-center justify-center shrink-0">
              <Cpu className="w-4 h-4 text-[#8a8a8a]" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-[10px] text-[#5a5a5a] font-mono uppercase mb-0.5">LLM Provider</div>
              <div className="flex gap-1">
                <button
                  onClick={() => setLlmProvider('gemini')}
                  className={`flex-1 px-1 py-0.5 text-[9px] font-mono uppercase tracking-wider border transition-all ${
                    llmProvider === 'gemini'
                      ? 'bg-[#2196f3]/15 border-[#2196f3]/50 text-[#2196f3]'
                      : 'bg-[#141414] border-[#2e2e2e] text-[#5a5a5a] hover:text-[#8a8a8a] hover:border-[#3e3e3e]'
                  }`}
                >
                  Gemini
                </button>
                <button
                  onClick={() => setLlmProvider('ollama')}
                  className={`flex-1 px-1 py-0.5 text-[9px] font-mono uppercase tracking-wider border transition-all ${
                    llmProvider === 'ollama'
                      ? 'bg-emerald-500/15 border-emerald-500/50 text-emerald-400'
                      : 'bg-[#141414] border-[#2e2e2e] text-[#5a5a5a] hover:text-[#8a8a8a] hover:border-[#3e3e3e]'
                  }`}
                >
                  Qwen 7B
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Live Risk Score Box */}
        <div className="bg-[#0e0e0e] border border-[#1e1e1e] p-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-sm bg-[#141414] border border-[#2e2e2e] flex items-center justify-center shrink-0">
              <Activity className="w-4 h-4 text-[#2196f3]" />
            </div>
            <div>
              <div className="text-[10px] text-[#5a5a5a] font-mono uppercase">Live Risk Score</div>
              <div className="text-sm font-mono font-medium text-[#2196f3]">{riskScore.toFixed(2)} / 1.00</div>
            </div>
          </div>
        </div>

        {/* Policy Status Box */}
        <div className="bg-[#0e0e0e] border border-[#1e1e1e] p-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-8 h-8 rounded-sm border flex items-center justify-center shrink-0 ${
              isBlocked ? 'bg-red-950/30 border-red-900 text-red-500' :
              riskScore > 0.6 ? 'bg-amber-950/30 border-amber-900 text-amber-500' :
              'bg-green-950/30 border-green-900 text-green-500'
            }`}>
              {isBlocked ? <ShieldAlert className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
            </div>
            <div>
              <div className="text-[10px] text-[#5a5a5a] font-mono uppercase">Policy Status</div>
              <div className={`text-sm font-mono font-medium ${
                isBlocked ? 'text-red-500' :
                riskScore > 0.6 ? 'text-amber-500' :
                'text-green-500'
              }`}>
                {isBlocked ? 'RESTRICTED' : 'ENFORCING'}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Workspace (Chat) */}
      <div className="flex-1 min-h-0 bg-[#0a0a0a] border border-[#1e1e1e] shadow-2xl overflow-hidden flex flex-col relative z-10">
        <ChatPanel messages={messages} loading={loading} error={error} onSendMessage={sendMessage} />
      </div>
    </div>
  );
}
