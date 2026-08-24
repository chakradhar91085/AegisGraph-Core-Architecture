import { useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import { useGraphState } from '../hooks/useGraphState';
import { ChatPanel } from '../components/ChatPanel';
import { SecurityPanel } from '../components/SecurityPanel';
import { GraphVisualization } from '../components/GraphVisualization';
import type { TelemetryEvent } from '../api';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, RefreshCw, ArrowLeft } from 'lucide-react';

export function DashboardPage() {
  const { messages, loading, error, sendMessage, clearSession } = useChat();
  const { graph, addGraphData, clearGraphState } = useGraphState();
  const navigate = useNavigate();

  // Extract telemetry history from agent messages
  const telemetryHistory = messages
    .filter(m => m.sender === 'agent' && m.telemetry)
    .map(m => m.telemetry!) as TelemetryEvent[];

  const currentTelemetry = telemetryHistory.length > 0 
    ? telemetryHistory[telemetryHistory.length - 1] 
    : null;

  useEffect(() => {
    const lastMsg = messages[messages.length - 1];
    if (lastMsg && lastMsg.sender === 'agent' && lastMsg.graph_data) {
      addGraphData(lastMsg.graph_data);
    } else if (lastMsg && lastMsg.sender === 'agent' && !lastMsg.graph_data) {
      // If it's a response with no graph data, pass undefined to clear 'isNew' flags
      addGraphData(undefined);
    }
  }, [messages, addGraphData]);

  const handleClearSession = () => {
    clearSession();
    clearGraphState();
  };

  return (
    <div className="h-screen w-screen bg-slate-50 flex flex-col font-sans overflow-hidden">
      
      {/* Top Navbar */}
      <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6 text-white shrink-0">
        <div className="flex items-center space-x-6">
          <button 
            onClick={() => navigate('/')}
            className="flex items-center text-slate-400 hover:text-white transition-colors text-sm font-medium"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Exit
          </button>
          
          <div className="h-6 w-px bg-slate-700"></div>

          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-blue-600 rounded-sm flex items-center justify-center">
              <ShieldCheck className="w-4 h-4 text-white" />
            </div>
            <h1 className="text-lg font-bold tracking-tight">AegisGraph Dashboard</h1>
          </div>

          <div className="flex items-center space-x-2 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700/50">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-xs text-slate-300 font-medium">Security Active</span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {error && (
            <div className="text-sm text-red-400 bg-red-900/30 px-3 py-1.5 rounded border border-red-900/50">
              {error}
            </div>
          )}
          <button 
            onClick={handleClearSession}
            className="flex items-center space-x-2 text-sm px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-slate-700"
          >
            <RefreshCw className="w-4 h-4" />
            <span>New Session</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden p-6 gap-6 max-w-[1800px] mx-auto w-full">
        
        {/* Left Column: Chat */}
        <div className="w-1/2 flex-shrink-0 flex flex-col h-full shadow-sm rounded-xl overflow-hidden border border-slate-200 bg-white">
          <ChatPanel 
            messages={messages} 
            loading={loading} 
            onSendMessage={sendMessage}
          />
        </div>

        {/* Right Column: Split Top/Bottom for Graph and Security */}
        <div className="flex-1 min-w-[450px] flex flex-col h-full gap-6">
          
          {/* Top Right: Graph Visualization */}
          <div className="flex-1 shadow-sm rounded-xl overflow-hidden border border-slate-200 bg-white flex flex-col">
            <div className="px-4 py-3 border-b border-slate-100 bg-slate-50 flex items-center justify-between shrink-0">
              <h2 className="text-sm font-semibold text-slate-700 flex items-center">
                <span className="w-2 h-2 rounded-full bg-blue-500 mr-2"></span>
                Graph Exploration
              </h2>
              <span className="text-xs text-slate-400 font-medium">{graph.nodes.length} nodes</span>
            </div>
            <div className="flex-1 relative">
              <GraphVisualization graphState={graph} telemetry={currentTelemetry} />
            </div>
          </div>

          {/* Bottom Right: Security Telemetry */}
          <div className="h-[400px] shrink-0 flex flex-col shadow-sm rounded-xl overflow-hidden border border-slate-800 bg-slate-900">
            <SecurityPanel telemetry={currentTelemetry} history={telemetryHistory} />
          </div>

        </div>

      </main>
    </div>
  );
}
