import { ThreatBanner } from './ThreatBanner'
import { DemoControlBar } from './DemoControlBar'
import { EventFeed } from './EventFeed'
import { MapPanel } from './MapPanel'
import { NarrativeTimeline } from './NarrativeTimeline'
import { BriefPanel } from './BriefPanel'

export function DashboardLayout() {
  return (
    <div className="h-screen grid grid-cols-[320px_1fr_360px] grid-rows-[48px_36px_1fr_200px] bg-slate-50">
      {/* Threat Status Banner - Top, full width */}
      <ThreatBanner />

      {/* Demo Control Bar - Below banner, full width */}
      <div style={{ gridArea: '2 / 1 / 3 / 4' }}>
        <DemoControlBar />
      </div>

      {/* Event Feed Panel - Left */}
      <div
        className="border-r border-slate-200"
        style={{ gridArea: '3 / 1 / 5 / 2' }}
      >
        <EventFeed />
      </div>

      {/* Map Panel - Center */}
      <div style={{ gridArea: '3 / 2 / 4 / 3' }}>
        <MapPanel />
      </div>

      {/* Narrative Timeline Panel - Bottom center */}
      <div style={{ gridArea: '4 / 2 / 5 / 3' }}>
        <NarrativeTimeline />
      </div>

      {/* Intelligence Brief Sidebar - Right */}
      <div className="border-l border-slate-200" style={{ gridArea: '3 / 3 / 5 / 4' }}>
        <BriefPanel />
      </div>
    </div>
  )
}
