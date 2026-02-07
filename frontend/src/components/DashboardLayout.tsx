import { ThreatBanner } from './ThreatBanner'
import { EventFeed } from './EventFeed'
import { MapPanel } from './MapPanel'
import { NarrativeTimeline } from './NarrativeTimeline'

export function DashboardLayout() {
  return (
    <div className="h-screen grid grid-cols-[320px_1fr_360px] grid-rows-[48px_1fr_200px]">
      {/* Threat Status Banner - Top, full width */}
      <ThreatBanner />

      {/* Event Feed Panel - Left */}
      <div
        className="border-r border-gray-200"
        style={{ gridArea: '2 / 1 / 4 / 2' }}
      >
        <EventFeed />
      </div>

      {/* Map Panel - Center */}
      <MapPanel />

      {/* Narrative Timeline Panel - Bottom center */}
      <div style={{ gridArea: '3 / 2 / 4 / 3' }}>
        <NarrativeTimeline />
      </div>

      {/* Intelligence Brief Sidebar - Right */}
      <div
        className="bg-white border-l border-gray-200 overflow-y-auto"
        style={{ gridArea: '2 / 3 / 4 / 4' }}
      >
        <div className="p-4">
          <div className="text-sm font-semibold text-gray-700 mb-2">
            INTELLIGENCE BRIEF PANEL
          </div>
          <div className="text-xs text-gray-500">
            Assessment, evidence, timeline, collection priorities
          </div>
        </div>
      </div>
    </div>
  )
}
