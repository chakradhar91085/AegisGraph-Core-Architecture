import { useRef, useEffect, useState, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import type { GraphState } from '../hooks/useGraphState';
import type { TelemetryEvent } from '../api';

interface GraphVisualizationProps {
  graphState: GraphState;
  telemetry: TelemetryEvent | null;
}

export function GraphVisualization({ graphState, telemetry }: GraphVisualizationProps) {
  const fgRef = useRef<any>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.offsetWidth,
        height: containerRef.current.offsetHeight,
      });
    }

    const handleResize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // When new nodes arrive, optionally auto-center the graph if needed
  useEffect(() => {
    if (fgRef.current && graphState.nodes.length > 0) {
      // Small timeout to allow physics to settle briefly before fitting
      setTimeout(() => {
        fgRef.current?.zoomToFit(400, 50);
      }, 1000);
    }
  }, [graphState.nodes.length]);

  if (graphState.nodes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-400 p-8 text-center bg-slate-50/50 rounded-lg">
        <div className="w-16 h-16 mb-4 rounded-full bg-slate-100 flex items-center justify-center">
          <svg className="w-8 h-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <p className="text-sm font-medium text-slate-500 mb-1">No graph data</p>
        <p className="text-xs">Ask about communication, connections, organizations, or topical relationships to explore the permitted knowledge graph.</p>
      </div>
    );
  }

  // Format data for react-force-graph (it expects 'links' instead of 'edges')
  const graphData = useMemo(() => {
    return {
      nodes: graphState.nodes.map(n => ({ ...n })),
      links: graphState.edges.map(e => ({ ...e }))
    };
  }, [graphState]);

  const riskLevel = telemetry?.policy?.risk_level || 'LOW';

  let activeColor = '#3b82f6'; // blue-500
  let activeGlow = 'rgba(219, 234, 254, 0.8)'; // blue-100
  let activeLink = 'rgba(59, 130, 246, 0.4)';
  let borderColor = 'border-slate-200';

  if (riskLevel === 'MEDIUM') {
    activeColor = '#f59e0b'; // amber-500
    activeGlow = 'rgba(253, 230, 138, 0.8)'; // amber-200
    activeLink = 'rgba(245, 158, 11, 0.4)';
    borderColor = 'border-amber-500/50 bg-amber-50/10';
  } else if (riskLevel === 'HIGH') {
    activeColor = '#ef4444'; // red-500
    activeGlow = 'rgba(254, 202, 202, 0.8)'; // red-200
    activeLink = 'rgba(239, 68, 68, 0.4)';
    borderColor = 'border-red-500/50 bg-red-50/10 shadow-[inset_0_0_15px_rgba(239,68,68,0.1)]';
  }

  const inactiveColor = '#94a3b8'; // slate-400
  const inactiveLink = 'rgba(148, 163, 184, 0.2)';

  return (
    <div className={`w-full h-full relative rounded-lg overflow-hidden border ${borderColor} transition-colors duration-500`} ref={containerRef}>
      <ForceGraph2D
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={graphData}
        nodeLabel="label"
        nodeColor={(node: any) => node.isNew ? activeColor : inactiveColor}
        nodeRelSize={6}
        linkColor={(link: any) => link.isNew ? activeLink : inactiveLink}
        linkWidth={(link: any) => link.isNew ? 2 : 1}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        cooldownTicks={100}
        onNodeDragEnd={node => {
          node.fx = node.x;
          node.fy = node.y;
        }}
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          if (node.x === undefined || node.y === undefined) return;

          const label = node.label || "";
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          
          if (node.isNew) {
            const t = Date.now();
            const pulseRadius = 5 + Math.sin(t / 150) * 1.5;
            const pulseOpacity = 0.4 + Math.sin(t / 150) * 0.2;
            
            ctx.beginPath();
            ctx.fillStyle = activeGlow.replace('0.8', pulseOpacity.toString());
            ctx.arc(node.x, node.y, pulseRadius, 0, 2 * Math.PI, false);
            ctx.fill();
          }
          
          ctx.beginPath();
          ctx.fillStyle = node.isNew ? activeColor : inactiveColor;
          ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI, false);
          ctx.fill();

          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = '#334155';
          ctx.fillText(label, node.x, node.y + 8 + fontSize/2);
        }}
      />
      <div className="absolute bottom-4 left-4 bg-white/90 px-3 py-2 rounded shadow-sm border border-slate-200 text-xs flex flex-col gap-1 pointer-events-none">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: activeColor }}></div>
          <span className="text-slate-600 font-medium">New in current query</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-slate-400"></div>
          <span className="text-slate-600 font-medium">Previously explored</span>
        </div>
      </div>
    </div>
  );
}
