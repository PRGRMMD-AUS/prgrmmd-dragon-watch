import { useEffect, useState } from 'react'
import { useAlerts } from '../hooks/useAlerts'
import type { ThreatLevel } from '../types/database'

function getCurrentTimeString(): string {
  const now = new Date()
  const hours = now.getUTCHours().toString().padStart(2, '0')
  const minutes = now.getUTCMinutes().toString().padStart(2, '0')
  const seconds = now.getUTCSeconds().toString().padStart(2, '0')
  return `${hours}:${minutes}:${seconds}Z`
}

export function ThreatBanner() {
  const { alert, loading } = useAlerts()
  const [isPulsing, setIsPulsing] = useState(false)
  const [prevLevel, setPrevLevel] = useState<ThreatLevel | null>(null)
  const [time, setTime] = useState(getCurrentTimeString)

  useEffect(() => {
    const interval = setInterval(() => setTime(getCurrentTimeString()), 1000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (alert?.threat_level && alert.threat_level !== prevLevel) {
      if (prevLevel !== null) {
        setIsPulsing(true)
        setTimeout(() => setIsPulsing(false), 2000)
      }
      setPrevLevel(alert.threat_level)
    }
  }, [alert?.threat_level, prevLevel])

  const getIndicator = () => {
    if (loading || !alert?.threat_level) return { dot: 'bg-[var(--text-dim)]', text: 'text-[var(--text-muted)]' }
    switch (alert.threat_level) {
      case 'GREEN': return { dot: 'bg-[var(--threat-low)]', text: 'text-[var(--text-muted)]' }
      case 'AMBER': return { dot: 'bg-[var(--threat-med)]', text: 'text-[var(--threat-med)]' }
      case 'RED': return { dot: 'bg-[var(--accent)]', text: 'text-[var(--accent)]' }
      default: return { dot: 'bg-[var(--text-dim)]', text: 'text-[var(--text-muted)]' }
    }
  }

  const getText = () => {
    if (loading) return 'INITIALIZING...'
    if (!alert?.threat_level) return 'THREAT LEVEL: NOMINAL'
    const confidence = Math.round(alert.confidence || 0)
    return `THREAT LEVEL: ${alert.threat_level} \u2014 ${confidence}%`
  }

  const indicator = getIndicator()

  return (
    <div
      className={`col-span-3 flex items-center justify-between px-6 bg-[var(--bg-panel)] border-b border-[var(--border-glass)] ${isPulsing ? 'animate-pulse-subtle' : ''} transition-all duration-500`}
      style={{ gridArea: '1 / 1 / 2 / 4', height: '40px' }}
    >
      <div className="flex items-center gap-2.5">
        <div className={`w-1.5 h-1.5 rounded-full ${indicator.dot}`} />
        <div className={`text-[10px] font-medium uppercase tracking-[0.2em] font-mono tabular-nums ${indicator.text}`}>
          {getText()}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-[10px] font-mono text-[var(--text-dim)] uppercase tracking-wider">UTC</span>
        <span className="text-[11px] font-mono text-[var(--text-secondary)] tabular-nums">{time}</span>
      </div>
    </div>
  )
}
