import { DashboardProvider, useDashboard } from '../context/DashboardContext'
import { ThreatBanner } from './ThreatBanner'
import { EventFeed } from './EventFeed'
import { MapPanel } from './MapPanel'
import { NarrativeTimeline } from './NarrativeTimeline'
import { BriefPanel } from './BriefPanel'

function Toast() {
  const { toast } = useDashboard()
  if (!toast) return null

  return (
    <div className="fixed top-3 right-3 z-50 glass-strong px-4 py-2.5 animate-slideInRight">
      <div className="flex items-center gap-2.5">
        <div className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]" />
        <span className="text-[10px] text-[var(--text-primary)] font-mono uppercase tracking-[0.15em]">
          {toast}
        </span>
      </div>
    </div>
  )
}

function DashboardGrid() {
  return (
    <div className="h-screen grid grid-cols-[320px_1fr_360px] grid-rows-[40px_1fr_200px] bg-[var(--bg-base)]">
      <ThreatBanner />

      <div
        className="border-r border-[var(--border-glass)]"
        style={{ gridArea: '2 / 1 / 4 / 2' }}
      >
        <EventFeed />
      </div>

      <div style={{ gridArea: '2 / 2 / 3 / 3' }}>
        <MapPanel />
      </div>

      <div style={{ gridArea: '3 / 2 / 4 / 3' }}>
        <NarrativeTimeline />
      </div>

      <div className="border-l border-[var(--border-glass)]" style={{ gridArea: '2 / 3 / 4 / 4' }}>
        <BriefPanel />
      </div>

      <Toast />
    </div>
  )
}

export function DashboardLayout() {
  return (
    <DashboardProvider>
      <DashboardGrid />
    </DashboardProvider>
  )
}
