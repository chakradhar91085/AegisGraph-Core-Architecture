import { useEffect, useRef, useState } from 'react';
import { useChat } from '../contexts/ChatContext';
import { GraphVisualizer } from './GraphVisualizer';
import type { GraphNode, GraphEdge } from './GraphVisualizer';
import { Maximize2, Minimize2 } from 'lucide-react';

export function NetworkGraph() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const visualizerRef = useRef<GraphVisualizer | null>(null);
  const { activeGraphData } = useChat();
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  useEffect(() => {
    if (!canvasRef.current) return;
    
    // Initialize the visualizer
    const visualizer = new GraphVisualizer(canvasRef.current, (node) => {
      console.log('Node clicked:', node);
    });
    
    visualizerRef.current = visualizer;
    
    return () => {
      visualizer.destroy();
      visualizerRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!visualizerRef.current) return;
    
    if (activeGraphData) {
      const latestData = activeGraphData;
      
      // We need to map the api nodes to the GraphNode expected by the engine
      // (They are essentially the same shape, but we cast to ensure type safety)
      const nodes: GraphNode[] = latestData.nodes.map(n => ({
        id: n.id,
        label: n.label,
        type: n.type
      }));
      
      const edges: GraphEdge[] = latestData.edges.map(e => ({
        source: e.source,
        target: e.target,
        relation: e.type,
      }));

      visualizerRef.current.setData(nodes, edges);
    }
  }, [activeGraphData]);
  
  // Handle resize when fullscreen toggles
  useEffect(() => {
    if (visualizerRef.current) {
      visualizerRef.current.resize();
    }
  }, [isFullscreen]);

  return (
    <div className={`relative flex flex-col bg-slate-950 border border-slate-800 rounded-lg shadow-lg overflow-hidden transition-all duration-300 ${isFullscreen ? 'fixed inset-4 z-50' : 'w-full h-full'}`}>
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 p-3 bg-gradient-to-b from-slate-950 to-transparent z-10 flex justify-between items-center pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto">
          <div className="text-xs font-mono font-medium text-blue-500 uppercase tracking-wider">
            Network Topology
          </div>
        </div>
        <button 
          className="p-1.5 bg-slate-800 border border-slate-700 text-slate-400 hover:text-slate-50 transition-colors rounded-md pointer-events-auto"
          onClick={() => setIsFullscreen(!isFullscreen)}
          title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
        >
          {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
        </button>
      </div>

      {/* Canvas Container */}
      <div className="flex-1 w-full h-full relative">
        <canvas 
          ref={canvasRef} 
          className="absolute inset-0 w-full h-full outline-none"
        />
        
        {/* Empty State Overlay */}
        {!activeGraphData && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center">
              <div className="text-slate-600 mb-2">
                <svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
              <div className="text-sm font-mono text-slate-500 uppercase">No Network Data Available</div>
              <div className="text-xs text-slate-600">Run a query to generate topology</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
