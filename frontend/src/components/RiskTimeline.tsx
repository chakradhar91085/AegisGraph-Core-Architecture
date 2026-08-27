import type { TelemetryEvent } from '../api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface RiskTimelineProps {
  history: TelemetryEvent[];
}

export function RiskTimeline({ history }: RiskTimelineProps) {
  if (!history || history.length === 0) {
    return (
      <div className="h-48 w-full flex items-center justify-center text-[#5a5a5a] text-xs font-mono uppercase tracking-widest border border-[#1e1e1e] bg-[#050505]">
        No telemetry history available
      </div>
    );
  }

  // Format data for Recharts
  const data = history.map((event, index) => ({
    query: `Q${index + 1}`,
    ewmaRisk: Number(event.smoothed_risk.toFixed(4)),
    instantRisk: Number(event.instantaneous_risk.toFixed(4)),
    blocked: event.blocked_by_policy,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      return (
        <div className="bg-[#0e0e0e] border border-[#1e1e1e] p-3 text-[10px] font-mono uppercase tracking-widest text-[#8a8a8a]">
          <p className="font-bold text-[#f2ede6] mb-2 border-b border-[#1e1e1e] pb-1">{label}</p>
          <p className="text-amber-500 mb-1">EWMA Risk: {dataPoint.ewmaRisk}</p>
          <p className="text-[#2196f3]">Instant Risk: {dataPoint.instantRisk}</p>
          {dataPoint.blocked && <p className="text-red-500 mt-2 font-bold bg-red-950/30 px-1 py-0.5 border border-red-900/50 inline-block">BLOCKED</p>}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-56 w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" vertical={false} />
          <XAxis 
            dataKey="query" 
            stroke="#5a5a5a" 
            fontSize={10} 
            fontFamily='"IBM Plex Mono", monospace'
            tickMargin={8} 
            axisLine={false} 
            tickLine={false}
          />
          <YAxis 
            domain={[0, 1]} 
            stroke="#5a5a5a" 
            fontSize={10} 
            fontFamily='"IBM Plex Mono", monospace'
            tickFormatter={(val) => val.toFixed(1)} 
            axisLine={false} 
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#1e1e1e', strokeWidth: 1, strokeDasharray: '4 4' }} />
          
          {/* Threshold references based on backend typical values */}
          <ReferenceLine y={0.25} stroke="#f59e0b" strokeOpacity={0.2} strokeDasharray="3 3" />
          <ReferenceLine y={0.7} stroke="#ef4444" strokeOpacity={0.2} strokeDasharray="3 3" />
          
          <Line 
            type="monotone" 
            dataKey="ewmaRisk" 
            stroke="#f59e0b" 
            strokeWidth={2} 
            dot={{ r: 3, strokeWidth: 1, fill: '#050505', stroke: '#f59e0b' }} 
            activeDot={{ r: 5, fill: '#f59e0b', stroke: '#050505', strokeWidth: 2 }} 
          />
          <Line 
            type="monotone" 
            dataKey="instantRisk" 
            stroke="#2196f3" 
            strokeWidth={1} 
            strokeDasharray="4 4"
            dot={false}
            activeDot={{ r: 3, fill: '#2196f3', stroke: '#050505', strokeWidth: 1 }} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
