import { cn } from '../lib/utils'
import { ThreatBanner } from './ThreatBanner'
import { EventFeed } from './EventFeed'

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
      <div
        className="bg-white border-b border-gray-200 flex items-center justify-center"
        style={{ gridArea: '2 / 2 / 3 / 3' }}
      >
        <div className="text-center">
          <div className="text-sm font-semibold text-gray-700 mb-1">
            MAP PANEL
          </div>
          <div className="text-xs text-gray-500">
            Interactive Taiwan Strait map
          </div>
        </div>
      </div>

      {/* Narrative Timeline Panel - Bottom center */}
      <div
        className="bg-gray-50 border-t border-gray-200"
        style={{ gridArea: '3 / 2 / 4 / 3' }}
      >
        <div className="p-4">
          <div className="text-sm font-semibold text-gray-700 mb-2">
            NARRATIVE TIMELINE PANEL
          </div>
          <div className="text-xs text-gray-500">
            Temporal correlation visualization
          </div>
        </div>
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
