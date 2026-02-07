import { useMemo } from 'react'
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

function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// Interpolate between green (#4ade80) and red (#e05a4f) based on score 0-100
function scoreToColor(score: number): string {
  const t = Math.min(1, Math.max(0, score / 100))
  // Green: 74, 222, 128 → Red: 224, 90, 79
  const r = Math.round(74 + (224 - 74) * t)
  const g = Math.round(222 + (90 - 222) * t)
  const b = Math.round(128 + (79 - 128) * t)
  return `rgb(${r}, ${g}, ${b})`
}

function scoreToLabel(score: number): string {
  if (score >= 70) return 'Critical'
  if (score >= 50) return 'High'
  if (score >= 30) return 'Elevated'
  return 'Normal'
}

export function NarrativeTimeline() {
  const { events, detectionHistory, loading } = useNarrativeEvents()

  const chartData = useMemo(() => {
    return detectionHistory.map((point) => ({
      time: formatTime(point.detected_at),
      score: point.score,
      level: point.level,
      fullTime: point.detected_at,
    }))
  }, [detectionHistory])

  const currentScore = chartData.length > 0 ? chartData[chartData.length - 1].score : 0
  const scoreColor = scoreToColor(currentScore)
  const scoreLabel = scoreToLabel(currentScore)

  const eventPoints = useMemo(() => {
    return events.map((event) => ({
      time: formatTime(event.detected_at),
      score: event.confidence * 100,
      summary: event.summary,
      fullTime: event.detected_at,
    }))
  }, [events])

  if (loading) {
    return (
      <div className="h-full bg-[var(--bg-panel)] border-t border-[var(--border-glass)] p-4">
        <h2 className="text-[10px] font-medium text-[var(--text-dim)] uppercase tracking-[0.15em] mb-3">
          Threat Score
        </h2>
        <div className="bg-white/[0.02] h-28 animate-pulse" />
      </div>
    )
  }

  if (detectionHistory.length === 0) {
    return (
      <div className="h-full bg-[var(--bg-panel)] border-t border-[var(--border-glass)] p-4 flex flex-col">
        <div className="flex items-center gap-3 mb-3 shrink-0">
          <h2 className="text-[10px] font-medium text-[var(--text-dim)] uppercase tracking-[0.15em]">
            Threat Score
          </h2>
          <span className="font-mono text-lg font-semibold tabular-nums text-[var(--text-dim)]">0</span>
        </div>
        <div className="flex-1 relative flex items-center justify-center min-h-0">
          <ResponsiveContainer width="100%" height="100%" minHeight={60}>
            <AreaChart data={[{ time: '00:00', score: 0 }, { time: '24:00', score: 0 }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.03)" />
              <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#3d3d3d' }} stroke="rgba(255, 255, 255, 0.04)" />
              <YAxis domain={[0, 100]} tick={{ fontSize: 9, fill: '#3d3d3d' }} stroke="rgba(255, 255, 255, 0.04)" />
              <Area type="monotone" dataKey="score" stroke="#2a2a2a" fill="#151515" fillOpacity={0.5} />
            </AreaChart>
          </ResponsiveContainer>
          <div className="absolute text-[10px] text-[var(--text-dim)] font-mono uppercase tracking-wider">
            Awaiting data...
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-[var(--bg-panel)] border-t border-[var(--border-glass)] p-4 flex flex-col">
      <div className="flex items-center gap-3 mb-3 shrink-0">
        <h2 className="text-[10px] font-medium text-[var(--text-dim)] uppercase tracking-[0.15em]">
          Threat Score
        </h2>
        <span className="font-mono text-lg font-semibold tabular-nums" style={{ color: scoreColor }}>
          {Math.round(currentScore)}
        </span>
        <div className="ml-auto flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full" style={{ background: scoreColor, opacity: 0.8 }} />
          <span className="text-[9px] font-mono text-[var(--text-dim)] uppercase">
            {scoreLabel}
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height="100%" minHeight={60}>
        <ComposedChart data={chartData}>
          <defs>
            {/* Green-to-red vertical gradient */}
            <linearGradient id="threatFill" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stopColor="#4ade80" stopOpacity={0.05} />
              <stop offset="30%" stopColor="#4ade80" stopOpacity={0.1} />
              <stop offset="50%" stopColor="#facc15" stopOpacity={0.12} />
              <stop offset="70%" stopColor="#e05a4f" stopOpacity={0.15} />
              <stop offset="100%" stopColor="#e05a4f" stopOpacity={0.25} />
            </linearGradient>
            {/* Stroke gradient matches */}
            <linearGradient id="threatStroke" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stopColor="#4ade80" />
              <stop offset="50%" stopColor="#facc15" />
              <stop offset="100%" stopColor="#e05a4f" />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.03)" />

          <XAxis
            dataKey="time"
            tick={{ fontSize: 9, fill: '#3d3d3d', fontFamily: 'JetBrains Mono, monospace' }}
            stroke="rgba(255, 255, 255, 0.04)"
            tickLine={false}
          />

          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 9, fill: '#3d3d3d', fontFamily: 'JetBrains Mono, monospace' }}
            stroke="rgba(255, 255, 255, 0.04)"
            tickLine={false}
            width={30}
          />

          {/* Normal threshold */}
          <ReferenceLine y={30} stroke="rgba(74, 222, 128, 0.15)" strokeDasharray="6 4" strokeWidth={0.5} />
          {/* Critical threshold */}
          <ReferenceLine y={70} stroke="rgba(224, 90, 79, 0.25)" strokeDasharray="6 4" strokeWidth={0.5} />

          <Area
            type="monotone"
            dataKey="score"
            stroke="url(#threatStroke)"
            strokeWidth={1.5}
            fill="url(#threatFill)"
            fillOpacity={1}
            animationDuration={600}
            animationEasing="ease-out"
            isAnimationActive={true}
          />

          {eventPoints.length > 0 && (
            <Scatter
              data={eventPoints}
              fill={scoreColor}
              shape="circle"
              dataKey="score"
              isAnimationActive={true}
              animationDuration={400}
            />
          )}

          <Tooltip
            contentStyle={{
              backgroundColor: '#0c0d0f',
              border: '1px solid rgba(255, 255, 255, 0.07)',
              borderRadius: '0',
              fontSize: '10px',
              fontFamily: 'JetBrains Mono, monospace',
              color: '#a3a3a3',
              padding: '8px 10px',
            }}
            formatter={(value: number, name?: string) => {
              if (name === 'score') {
                const color = scoreToColor(value)
                return [<span style={{ color }}>{value.toFixed(1)}</span>, 'Score']
              }
              return [value, name || '']
            }}
            labelStyle={{ color: '#3d3d3d', fontSize: '9px', marginBottom: '2px' }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
