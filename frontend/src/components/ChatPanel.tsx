import { useState, useRef, useEffect } from 'react';
import type { Message } from '../contexts/ChatContext';
import { Send, Loader2, ShieldBan, ShieldCheck, Cpu, Database, Activity, MessagesSquare } from 'lucide-react';
import clsx from 'clsx';

interface ChatPanelProps {
  messages: Message[];
  loading: boolean;
  error?: string | null;
  onSendMessage: (msg: string) => void;
}

const QUICK_START_QUERIES = [
  "What can I explore in this knowledge graph?",
  "Who are the employees?",
  "Who is Christopher Calger?",
  "What emails did he send?"
];

export function ChatPanel({ messages, loading, error, onSendMessage }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Auto-focus input when loading finishes
  useEffect(() => {
    if (!loading) {
      inputRef.current?.focus();
    }
  }, [loading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickStart = (query: string) => {
    if (loading) return;
    onSendMessage(query);
  };

  return (
    <div className="flex flex-col h-full bg-[#0a0a0a] relative">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-[#8a8a8a] animate-in fade-in duration-500">
            <div className="w-16 h-16 bg-[#0e0e0e] rounded-sm flex items-center justify-center mb-6 border border-[#1e1e1e]">
              <MessagesSquare className="w-8 h-8 text-[#2196f3]" />
            </div>
            <h2 className="text-xl font-display font-bold text-[#f2ede6] uppercase tracking-widest mb-2">AegisGraph Terminal</h2>
            <p className="text-center max-w-md mb-8 text-[#8a8a8a] leading-relaxed text-sm">
              Interact with the Enron knowledge graph. All queries are continuously monitored for behavioral anomalies and evaluated against adaptive security policies.
            </p>
            
            <div className="grid grid-cols-1 gap-3 w-full max-w-md">
              {QUICK_START_QUERIES.map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickStart(query)}
                  disabled={loading}
                  className="text-left px-4 py-3 bg-[#0e0e0e] border border-[#1e1e1e] hover:border-[#2196f3]/50 transition-colors text-sm text-[#f2ede6] font-medium flex items-center group disabled:opacity-50"
                >
                  <ArrowRightIcon className="w-4 h-4 mr-3 text-[#5a5a5a] group-hover:text-[#2196f3] transition-colors" />
                  {query}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {messages.map((msg) => {
          const isBlocked = msg.telemetry?.blocked_by_policy;
          const telemetry = msg.telemetry;
          
          return (
            <div 
              key={msg.id} 
              className={clsx(
                "max-w-[85%] rounded-sm p-4 shadow-sm",
                msg.sender === 'user' 
                  ? "bg-[#141414] text-[#f2ede6] self-end ml-auto border border-[#1e1e1e] border-r-2 border-r-[#2196f3]" 
                  : isBlocked
                    ? "bg-[#0e0e0e] text-red-500 border border-red-900/50 self-start w-full max-w-[90%]"
                    : "bg-[#0e0e0e] text-[#f2ede6] border border-[#1e1e1e] border-l-2 border-l-[#5a5a5a] self-start w-full max-w-[90%]"
              )}
            >
              {isBlocked && (
                <div className="flex items-center text-red-500 font-bold text-[11px] font-mono mb-3 uppercase tracking-[0.1em] bg-red-950/20 p-2 border border-red-900/30">
                  <ShieldBan className="w-4 h-4 mr-2" />
                  Request Blocked By Security Policy
                </div>
              )}
              
              <div className={clsx(
                "text-sm leading-relaxed whitespace-pre-wrap", 
                isBlocked ? "italic text-red-500/80 font-mono text-xs" : (msg.sender === 'user' ? "" : "text-[#c2c2c2]")
              )}>
                {msg.text}
              </div>

              {/* Sub-Metadata for Agent Responses */}
              {msg.sender === 'agent' && telemetry && !isBlocked && (
                <div className="mt-4 pt-3 border-t border-[#1e1e1e] flex flex-wrap gap-4 text-[10px] text-[#5a5a5a] font-mono uppercase tracking-[0.1em]">
                  {msg.llm_provider && (
                    <div className={`flex items-center px-1.5 py-0.5 rounded-sm ${
                      msg.llm_provider === 'ollama' 
                        ? 'bg-emerald-950/30 text-emerald-400 border border-emerald-900/40' 
                        : 'bg-blue-950/30 text-blue-400 border border-blue-900/40'
                    }`} title="LLM Provider">
                      {msg.llm_provider === 'ollama' ? 'Qwen 7B' : 'Gemini'}
                    </div>
                  )}
                  <div className="flex items-center" title="Records Retrieved">
                    <Database className="w-3 h-3 mr-1.5 text-[#8a8a8a]" />
                    {telemetry.result_count} records
                  </div>
                  <div className="flex items-center" title="Retrieval Strategy">
                    <Cpu className="w-3 h-3 mr-1.5 text-[#8a8a8a]" />
                    {telemetry.retrieval_strategy}
                  </div>
                  <div className="flex items-center" title="Instantaneous Risk">
                    <Activity className="w-3 h-3 mr-1.5 text-[#8a8a8a]" />
                    Risk: <span className="text-[#f2ede6] ml-1">{telemetry.instantaneous_risk.toFixed(2)}</span>
                  </div>
                  {telemetry.policy?.risk_level === 'MEDIUM' && (
                    <div className="flex items-center text-amber-500 bg-amber-950/20 px-2 py-0.5 border border-amber-900/30">
                      <ShieldCheck className="w-3 h-3 mr-1.5" />
                      Policy Constrained
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
        
        {loading && (
          <div className="bg-[#0e0e0e] border border-[#1e1e1e] border-l-2 border-l-[#2196f3] shadow-sm p-4 w-full max-w-[60%] flex items-center space-x-4">
            <div className="relative flex items-center justify-center w-6 h-6">
              <Loader2 className="w-4 h-4 animate-spin text-[#2196f3] absolute" />
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-mono uppercase tracking-[0.1em] text-[#f2ede6]">Analyzing Request...</span>
              <span className="text-[10px] text-[#5a5a5a] font-mono tracking-wider mt-0.5">Evaluating behavioral risk and retrieving context</span>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-950/20 border border-red-900/50 border-l-2 border-l-red-500 shadow-sm p-4 w-full max-w-[80%] flex items-center space-x-4">
            <div className="relative flex items-center justify-center w-6 h-6">
              <ShieldBan className="w-4 h-4 text-red-500 absolute" />
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-mono uppercase tracking-[0.1em] text-red-400">Connection Failed</span>
              <span className="text-[11px] text-red-500/80 font-mono mt-0.5">{error}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-[#0a0a0a] border-t border-[#1e1e1e] shrink-0 relative z-10">
        <form onSubmit={handleSubmit} className="relative flex items-end max-w-4xl mx-auto">
          <div className="absolute left-4 bottom-4 w-2 h-2 rounded-full bg-[#2196f3] animate-pulse"></div>
          <textarea
            ref={inputRef}
            className="w-full pl-10 pr-16 py-3.5 bg-[#0e0e0e] border border-[#1e1e1e] text-[#f2ede6] focus:outline-none focus:border-[#2196f3] resize-none overflow-hidden transition-colors font-mono text-sm"
            placeholder="ENTER QUERY..."
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            disabled={loading}
            style={{ minHeight: '52px', maxHeight: '150px' }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="absolute right-2 bottom-2 bg-[#141414] border border-[#1e1e1e] text-[#2196f3] p-2 hover:bg-[#2196f3] hover:text-[#050505] disabled:opacity-50 transition-colors flex items-center justify-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <div className="text-center mt-3">
          <span className="text-[10px] text-[#5a5a5a] font-mono uppercase tracking-[0.2em]">AegisGraph Security Intercept Active</span>
        </div>
      </div>
    </div>
  );
}

// Simple internal icon for quick starts
function ArrowRightIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12h14" />
      <path d="m12 5 7 7-7 7" />
    </svg>
  );
}
