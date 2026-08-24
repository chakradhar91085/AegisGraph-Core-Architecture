import { useState, useRef, useEffect } from 'react';
import type { Message } from '../hooks/useChat';
import { Send, Loader2, ShieldBan, ShieldCheck, Cpu, Database, Activity, MessagesSquare } from 'lucide-react';
import clsx from 'clsx';

interface ChatPanelProps {
  messages: Message[];
  loading: boolean;
  onSendMessage: (msg: string) => void;
}

const QUICK_START_QUERIES = [
  "What can I explore in this knowledge graph?",
  "Who are the employees?",
  "Who is Christopher Calger?",
  "What emails did he send?"
];

export function ChatPanel({ messages, loading, onSendMessage }: ChatPanelProps) {
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
    <div className="flex flex-col h-full bg-white relative">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 animate-in fade-in duration-500">
            <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mb-6 border border-blue-100">
              <MessagesSquare className="w-8 h-8 text-blue-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 mb-2">AegisGraph Secure Workspace</h2>
            <p className="text-center max-w-md mb-8 text-slate-500 leading-relaxed">
              Interact with the Enron knowledge graph. All queries are continuously monitored for behavioral anomalies and evaluated against adaptive security policies.
            </p>
            
            <div className="grid grid-cols-1 gap-3 w-full max-w-md">
              {QUICK_START_QUERIES.map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickStart(query)}
                  disabled={loading}
                  className="text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-all text-sm text-slate-700 font-medium flex items-center group disabled:opacity-50"
                >
                  <ArrowRightIcon className="w-4 h-4 mr-3 text-slate-400 group-hover:text-blue-500 transition-colors" />
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
                "max-w-[85%] rounded-2xl p-4 shadow-sm",
                msg.sender === 'user' 
                  ? "bg-blue-600 text-white self-end ml-auto rounded-tr-sm" 
                  : isBlocked
                    ? "bg-red-50 text-red-900 border border-red-200 rounded-tl-sm self-start w-full max-w-[90%]"
                    : "bg-white text-slate-800 border border-slate-200 rounded-tl-sm self-start w-full max-w-[90%]"
              )}
            >
              {isBlocked && (
                <div className="flex items-center text-red-700 font-bold text-sm mb-3 uppercase tracking-wider bg-red-100/50 p-2 rounded border border-red-200/50">
                  <ShieldBan className="w-5 h-5 mr-2" />
                  Request Blocked By Security Policy
                </div>
              )}
              
              <div className={clsx(
                "text-sm leading-relaxed whitespace-pre-wrap", 
                isBlocked ? "italic text-red-800/80 font-medium" : (msg.sender === 'user' ? "" : "text-slate-700")
              )}>
                {msg.text}
              </div>

              {/* Sub-Metadata for Agent Responses */}
              {msg.sender === 'agent' && telemetry && !isBlocked && (
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center space-x-4 text-[11px] text-slate-500 font-medium uppercase tracking-wider">
                  <div className="flex items-center" title="Records Retrieved">
                    <Database className="w-3.5 h-3.5 mr-1 text-slate-400" />
                    {telemetry.result_count} records
                  </div>
                  <div className="flex items-center" title="Retrieval Strategy">
                    <Cpu className="w-3.5 h-3.5 mr-1 text-slate-400" />
                    {telemetry.retrieval_strategy}
                  </div>
                  <div className="flex items-center" title="Instantaneous Risk">
                    <Activity className="w-3.5 h-3.5 mr-1 text-slate-400" />
                    Risk: {telemetry.instantaneous_risk.toFixed(2)}
                  </div>
                  {telemetry.policy?.risk_level === 'MEDIUM' && (
                    <div className="flex items-center text-amber-600 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                      <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                      Policy Constrained
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
        
        {loading && (
          <div className="bg-white border border-slate-200 shadow-sm rounded-2xl rounded-tl-sm p-4 w-full max-w-[60%] flex items-center space-x-4">
            <div className="relative flex items-center justify-center w-8 h-8">
              <Loader2 className="w-6 h-6 animate-spin text-blue-500 absolute" />
              <div className="w-3 h-3 bg-blue-100 rounded-full"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-slate-700">Analyzing Request...</span>
              <span className="text-xs text-slate-500">Evaluating behavioral risk and retrieving context</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-slate-200 shrink-0 relative z-10">
        <form onSubmit={handleSubmit} className="relative flex items-end">
          <textarea
            ref={inputRef}
            className="w-full px-5 py-4 pr-16 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 resize-none overflow-hidden transition-shadow"
            placeholder="Query the Enron dataset securely..."
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
            style={{ minHeight: '56px', maxHeight: '150px' }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="absolute right-2 bottom-2 bg-blue-600 text-white p-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center justify-center shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <div className="text-center mt-3">
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">AegisGraph intercepts all queries before LLM generation.</span>
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
