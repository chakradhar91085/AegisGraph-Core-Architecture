import { ShieldAlert, Fingerprint, RefreshCcw, ChevronDown, ChevronRight, Activity, Clock } from 'lucide-react';
import { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { auditApi } from '../api';
import type { AuditSession, AuditQuery } from '../api';

export function SystemLogs() {
  const [sessions, setSessions] = useState<AuditSession[]>([]);
  const [expandedSession, setExpandedSession] = useState<string | null>(null);
  const [sessionQueries, setSessionQueries] = useState<Record<string, AuditQuery[]>>({});
  const [loading, setLoading] = useState(true);
  const [denied, setDenied] = useState(false);
  
  // Use a ref to track if we should keep polling
  const isMounted = useRef(true);

  const fetchSessions = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      const data = await auditApi.getSessions(50);
      setSessions(data);
      setDenied(false);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 403) setDenied(true);
      console.error("Failed to fetch sessions:", err);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const loadQueries = async (sessionId: string) => {
    try {
      const queries = await auditApi.getSessionQueries(sessionId);
      setSessionQueries(prev => ({ ...prev, [sessionId]: queries }));
    } catch (err) {
      console.error("Failed to load queries:", err);
    }
  };

  const toggleSession = (sessionId: string) => {
    if (expandedSession === sessionId) {
      setExpandedSession(null);
    } else {
      setExpandedSession(sessionId);
      loadQueries(sessionId);
    }
  };

  // Poll for updates if there's an ACTIVE session
  useEffect(() => {
    isMounted.current = true;
    fetchSessions();
    
    const interval = setInterval(() => {
      if (isMounted.current) {
        // Or if we just want to keep logs fresh
        fetchSessions(true);
        if (expandedSession) {
          loadQueries(expandedSession);
        }
      }
    }, 5000);
    
    return () => {
      isMounted.current = false;
      clearInterval(interval);
    };
  }, [expandedSession]); // eslint-disable-line react-hooks/exhaustive-deps

  const getSeverityColor = (mode: string) => {
    switch(mode) {
      case 'BLOCK': return 'text-red-500 border-red-900/50 bg-red-950/30';
      case 'MASK': 
      case 'RESTRICT': return 'text-amber-500 border-amber-900/50 bg-amber-950/30';
      case 'ALLOW': return 'text-green-500 border-green-900/50 bg-green-950/30';
      default: return 'text-gray-500 border-gray-800 bg-gray-900/30';
    }
  };
  
  const getOutcomeColor = (outcome: string) => {
    switch(outcome) {
      case 'BLOCKED': return 'text-red-500';
      case 'MASKED': 
      case 'ATTENUATED': return 'text-amber-500';
      case 'PERMITTED': return 'text-green-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#050505] p-6 w-full mx-auto relative overflow-hidden">
      {/* Header */}
      <div className="mb-6 flex items-end justify-between z-10 shrink-0">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-display font-bold text-[#f2ede6] uppercase tracking-wide">System Logs</h1>
            <div className="sys-tag">Audit</div>
          </div>
          <p className="text-sm text-[#8a8a8a] font-mono tracking-tight">
            AEGISGRAPH // FORENSIC SECURITY TRAIL
          </p>
        </div>
        <button onClick={() => fetchSessions(false)} className="flex items-center gap-2 text-xs font-mono text-[#2196f3] hover:text-[#f2ede6] transition-colors bg-[#0e0e0e] border border-[#1e1e1e] px-4 py-2">
          <RefreshCcw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> REFRESH
        </button>
      </div>
      
      <div className="flex-1 min-h-0 bg-[#0a0a0a] border border-[#1e1e1e] shadow-2xl flex flex-col relative z-10 overflow-hidden">
        {sessions.length === 0 && !loading ? (
          <div className="flex-1 flex flex-col items-center justify-center text-[#5a5a5a] p-8 text-center relative">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9IiMzMzMiLz48L3N2Zz4=')] opacity-20 pointer-events-none"></div>
            
            <div className="w-16 h-16 mb-4 rounded-sm border border-[#1e1e1e] bg-[#0e0e0e] flex items-center justify-center z-10">
              <ShieldAlert className="w-8 h-8 text-[#2196f3] opacity-50" />
            </div>
            <p className="text-sm font-display uppercase tracking-widest text-[#8a8a8a] mb-1 z-10">No Audit Events Found</p>
            <p className="text-xs font-mono max-w-md text-center z-10">
              {denied ? 'Audit logs are restricted to the Auditor role.' : 'The PostgreSQL audit log is currently empty. Run some queries to generate telemetry.'}
            </p>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-4 z-10">
            <div className="mb-4">
              <span className="text-xs font-mono text-[#8a8a8a]">SHOWING LATEST {sessions.length} SESSIONS</span>
            </div>
            
            <div className="w-full border border-[#1e1e1e] bg-[#050505] overflow-hidden text-left flex flex-col gap-2 p-2">
              {sessions.map((session) => {
                const isExpanded = expandedSession === session.session_id;
                const queries = sessionQueries[session.session_id] || [];
                
                const startStr = session.started_at ? new Date(session.started_at).toLocaleTimeString() : '--:--';
                const endStr = session.ended_at ? new Date(session.ended_at).toLocaleTimeString() : 'ACTIVE';
                const duration = session.ended_at && session.started_at 
                  ? `${Math.round((new Date(session.ended_at).getTime() - new Date(session.started_at).getTime()) / 1000)}s` 
                  : '...';

                return (
                  <div key={session.session_id} className="border border-[#1e1e1e] bg-[#0a0a0a] rounded-sm overflow-hidden flex flex-col">
                    {/* Session Header Row */}
                    <div 
                      onClick={() => toggleSession(session.session_id)}
                      className={`grid grid-cols-12 gap-4 p-3 items-center cursor-pointer hover:bg-[#141414] transition-colors ${isExpanded ? 'bg-[#141414] border-b border-[#1e1e1e]' : ''}`}
                    >
                      <div className="col-span-1 flex items-center justify-center text-[#5a5a5a]">
                        {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                      </div>
                      
                      <div className="col-span-3 flex flex-col">
                        <span className="text-xs font-mono text-[#f2ede6] truncate flex items-center gap-2">
                          <Fingerprint className="w-3 h-3 text-[#2196f3]" />
                          {session.session_id.substring(0, 8)}...
                        </span>
                        <span className="text-[10px] font-mono text-[#5a5a5a]">Role: {session.role}</span>
                      </div>
                      
                      <div className="col-span-2 flex flex-col text-[10px] font-mono text-[#8a8a8a]">
                        <span className="flex items-center gap-1"><Clock className="w-3 h-3"/> {startStr} - {endStr}</span>
                        <span>{session.query_count} queries ({duration})</span>
                      </div>
                      
                      <div className="col-span-2 flex flex-col text-[10px] font-mono">
                        <span className="text-[#8a8a8a]">Peak Risk: <span className="text-[#f2ede6]">{session.peak_risk_score.toFixed(2)}</span></span>
                        <span className="text-[#8a8a8a]">Final Risk: <span className="text-[#f2ede6]">{session.final_risk_score.toFixed(2)}</span></span>
                      </div>
                      
                      <div className="col-span-2 flex items-center">
                        <div className="flex flex-col gap-1">
                          <span className="text-[9px] text-[#5a5a5a] uppercase">Highest Mode</span>
                          <span className={`px-2 py-0.5 border text-[10px] flex items-center gap-1 w-max ${getSeverityColor(session.highest_behavioral_mode)}`}>
                            {session.highest_behavioral_mode}
                          </span>
                        </div>
                      </div>
                      
                      <div className="col-span-2 flex items-center justify-end">
                        {session.status === 'ACTIVE' ? (
                          <span className="px-2 py-1 bg-green-900/20 text-green-500 border border-green-500/30 text-[10px] font-mono flex items-center gap-1 animate-pulse">
                            <Activity className="w-3 h-3"/> ACTIVE
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-[#1e1e1e] text-[#8a8a8a] text-[10px] font-mono">
                            COMPLETED
                          </span>
                        )}
                      </div>
                    </div>
                    
                    {/* Expanded Queries List */}
                    {isExpanded && (
                      <div className="p-0 bg-[#050505]">
                        <div className="grid grid-cols-12 gap-2 p-2 border-b border-[#1e1e1e] text-[9px] font-mono text-[#5a5a5a] uppercase tracking-widest bg-[#0e0e0e]">
                          <div className="col-span-1">TIME</div>
                          <div className="col-span-1">RISK</div>
                          <div className="col-span-2">BEHAVIORAL MODE</div>
                          <div className="col-span-2">ACTUAL OUTCOME</div>
                          <div className="col-span-1">RESULTS</div>
                          <div className="col-span-5">QUERY TEXT</div>
                        </div>
                        
                        {queries.length === 0 ? (
                          <div className="p-4 text-center text-xs font-mono text-[#5a5a5a]">Loading queries...</div>
                        ) : (
                          queries.map((q) => {
                            const timeStr = q.timestamp ? new Date(q.timestamp).toLocaleTimeString() : '';
                            return (
                              <div key={q.id} className="grid grid-cols-12 gap-2 p-2 border-b border-[#1e1e1e]/50 text-[11px] font-mono items-center hover:bg-[#111] transition-colors">
                                <div className="col-span-1 text-[#5a5a5a]">{timeStr}</div>
                                <div className="col-span-1 text-[#f2ede6]">{q.risk_score.toFixed(2)}</div>
                                
                                <div className="col-span-2">
                                  <span className={`px-1.5 py-0.5 border text-[9px] w-max ${getSeverityColor(q.behavioral_mode)}`}>
                                    {q.behavioral_mode}
                                  </span>
                                </div>
                                
                                <div className="col-span-2">
                                  <span className={`font-bold ${getOutcomeColor(q.retrieval_outcome)}`}>
                                    {q.retrieval_outcome}
                                  </span>
                                </div>
                                
                                <div className="col-span-1 text-[#8a8a8a]">{q.result_count}</div>
                                <div className="col-span-5 text-[#8a8a8a] truncate" title={q.query}>{q.query}</div>
                              </div>
                            );
                          })
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
