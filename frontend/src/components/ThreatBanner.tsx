import { useEffect, useState } from 'react'
import { useAlerts } from '../hooks/useAlerts'
import type { ThreatLevel } from '../types/database'

export function ThreatBanner() {
  const { alert, loading } = useAlerts()
  const [isPulsing, setIsPulsing] = useState(false)
  const [prevLevel, setPrevLevel] = useState<ThreatLevel | null>(null)

  // Detect threat level changes and trigger pulse animation
  useEffect(() => {
    if (alert?.threat_level && alert.threat_level !== prevLevel) {
      if (prevLevel !== null) {
        // Only pulse on escalation, not initial load
        setIsPulsing(true)
        setTimeout(() => setIsPulsing(false), 2000)
      }
      setPrevLevel(alert.threat_level)
    }
  }, [alert?.threat_level, prevLevel])

  // Determine background color based on threat level
  const getBackgroundClass = () => {
    if (loading || !alert?.threat_level) {
      return 'bg-slate-300'
    }

    switch (alert.threat_level) {
      case 'GREEN':
        return 'bg-emerald-500'
      case 'AMBER':
        return 'bg-amber-500'
      case 'RED':
        return 'bg-red-600'
      default:
        return 'bg-slate-300'
    }
  }

  const getText = () => {
    if (loading) {
      return 'INITIALIZING...'
    }

    if (!alert?.threat_level) {
      return 'THREAT LEVEL: GREEN — 0% confidence'
    }

    const level = alert.threat_level
    const confidence = Math.round(alert.confidence || 0)

    return `THREAT LEVEL: ${level} — ${confidence}% confidence`
  }

  return (
    <div
      className={`
        col-span-3 border-b border-slate-200 flex items-center justify-center px-6
        ${getBackgroundClass()}
        ${isPulsing ? 'animate-pulse' : ''}
      `}
      style={{ gridArea: '1 / 1 / 2 / 4', height: '48px' }}
    >
      <div className="text-sm font-bold text-white uppercase tracking-wider">
        {getText()}
      </div>
    </div>
  )
}
