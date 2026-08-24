import type { TelemetryEvent } from '../api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface RiskTimelineProps {
  history: TelemetryEvent[];
}

export function RiskTimeline({ history }: RiskTimelineProps) {
  if (!history || history.length === 0) {
    return (
      <div className="h-48 w-full flex items-center justify-center text-slate-500 text-sm border border-slate-800 rounded bg-slate-900/50">
        No telemetry history available yet.
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
        <div className="bg-slate-800 border border-slate-700 p-3 rounded shadow-lg text-xs font-mono text-slate-300">
          <p className="font-bold text-white mb-1">{label}</p>
          <p className="text-amber-400">EWMA Risk: {dataPoint.ewmaRisk}</p>
          <p className="text-blue-400">Instant Risk: {dataPoint.instantRisk}</p>
          {dataPoint.blocked && <p className="text-red-500 mt-1 font-bold">BLOCKED</p>}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-56 w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis 
            dataKey="query" 
            stroke="#64748b" 
            fontSize={10} 
            tickMargin={8} 
            axisLine={false} 
            tickLine={false}
          />
          <YAxis 
            domain={[0, 1]} 
            stroke="#64748b" 
            fontSize={10} 
            tickFormatter={(val) => val.toFixed(1)} 
            axisLine={false} 
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Threshold references based on backend typical values */}
          <ReferenceLine y={0.25} stroke="#f59e0b" strokeOpacity={0.3} strokeDasharray="3 3" />
          <ReferenceLine y={0.7} stroke="#ef4444" strokeOpacity={0.3} strokeDasharray="3 3" />
          
          <Line 
            type="monotone" 
            dataKey="ewmaRisk" 
            stroke="#f59e0b" 
            strokeWidth={3} 
            dot={{ r: 4, strokeWidth: 2, fill: '#0f172a' }} 
            activeDot={{ r: 6 }} 
          />
          <Line 
            type="monotone" 
            dataKey="instantRisk" 
            stroke="#3b82f6" 
            strokeWidth={1} 
            strokeDasharray="4 4"
            dot={false}
            activeDot={{ r: 4 }} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
