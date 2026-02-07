import { useNarrativeEvents } from '../hooks/useNarrativeEvents'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ComposedChart,
} from 'recharts'

// Format timestamp for x-axis
function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

export function NarrativeTimeline() {
  const { events, detectionHistory, loading } = useNarrativeEvents()

  if (loading) {
    return (
      <div className="h-full bg-white border-t border-slate-200 p-4">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
          Narrative Correlation Timeline
        </h2>
        <div className="bg-slate-200 rounded h-32 animate-pulse" />
      </div>
    )
  }

  // If no detection history, show empty state
  if (detectionHistory.length === 0) {
    return (
      <div className="h-full bg-white border-t border-slate-200 p-4">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
          Narrative Correlation Timeline
        </h2>
        <div className="h-32 flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={[
                { time: '00:00', score: 0 },
                { time: '24:00', score: 0 },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="time" tick={{ fontSize: 10 }} stroke="#9ca3af" />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} stroke="#9ca3af" />
              <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" />
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" />
              <Area
                type="monotone"
                dataKey="score"
                stroke="#9ca3af"
                fill="#e5e7eb"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
          <div className="absolute text-sm text-slate-400">
            Awaiting correlation data...
          </div>
        </div>
      </div>
    )
  }

  // Prepare chart data from detection history
  const chartData = detectionHistory.map((point) => ({
    time: formatTime(point.detected_at),
    score: point.score,
    level: point.level,
    fullTime: point.detected_at,
  }))

  // Prepare narrative event scatter points
  const eventPoints = events.map((event) => ({
    time: formatTime(event.detected_at),
    score: event.confidence * 100, // Convert confidence (0-1) to score (0-100)
    summary: event.summary,
    fullTime: event.detected_at,
  }))

  return (
    <div className="h-full bg-white border-t border-slate-200 p-4">
      <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
        Narrative Correlation Timeline
      </h2>

      <ResponsiveContainer width="100%" height="85%">
        <ComposedChart data={chartData}>
          <defs>
            <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ef4444" stopOpacity={0.8} />
              <stop offset="40%" stopColor="#f59e0b" stopOpacity={0.6} />
              <stop offset="70%" stopColor="#10b981" stopOpacity={0.4} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

          <XAxis
            dataKey="time"
            tick={{ fontSize: 10 }}
            stroke="#9ca3af"
          />

          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 10 }}
            stroke="#9ca3af"
            label={{ value: 'Threat Score', angle: -90, position: 'insideLeft', fontSize: 10 }}
          />

          {/* Reference lines for threat level boundaries */}
          <ReferenceLine
            y={30}
            stroke="#10b981"
            strokeDasharray="3 3"
            strokeWidth={1}
          />
          <ReferenceLine
            y={70}
            stroke="#ef4444"
            strokeDasharray="3 3"
            strokeWidth={1}
          />

          {/* Area chart for threat score over time */}
          <Area
            type="monotone"
            dataKey="score"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#scoreGradient)"
            fillOpacity={0.6}
          />

          {/* Scatter points for narrative events */}
          {eventPoints.length > 0 && (
            <Scatter
              data={eventPoints}
              fill="#8b5cf6"
              shape="circle"
              dataKey="score"
            />
          )}

          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              fontSize: '12px',
            }}
            formatter={(value: any, name?: string) => {
              if (name === 'score') return [value.toFixed(1), 'Threat Score']
              return [value, name || '']
            }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
