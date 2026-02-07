import { useState } from 'react'
import { AlertTriangle, X, ChevronRight, ChevronDown, Send } from 'lucide-react'
import { useBriefs } from '../hooks/useBriefs'
import { useMovementEvents } from '../hooks/useMovementEvents'
import { useDashboard } from '../context/DashboardContext'
import type { ThreatLevel, MovementEvent } from '../types/database'

const threatStyles: Record<ThreatLevel, { text: string; dot: string }> = {
  GREEN: { text: 'text-[var(--text-muted)]', dot: 'bg-[var(--threat-low)]' },
  AMBER: { text: 'text-[var(--threat-med)]', dot: 'bg-[var(--threat-med)]' },
  RED: { text: 'text-[var(--accent)]', dot: 'bg-[var(--accent)]' },
}

const DEPARTMENTS = [
  {
    name: 'Naval Operations',
    members: ['Cdr. J. Mitchell', 'Lt. Cdr. R. Park', 'Lt. S. Huang'],
  },
  {
    name: 'Intelligence Division',
    members: ['Col. A. Torres', 'Maj. L. Chen', 'Capt. D. Williams'],
  },
  {
    name: 'Strategic Command',
    members: ['Gen. M. Harrison', 'Brig. K. Nakamura', 'Col. P. Adams'],
  },
  {
    name: 'Cyber Operations',
    members: ['Lt. Col. E. Shaw', 'Maj. T. Rivera', 'Capt. N. Kim'],
  },
]

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

function formatTime(detected_at: string): string {
  const d = new Date(detected_at)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function SectionHeader({ title }: { title: string }) {
  return (
    <h3 className="text-[10px] font-medium text-[var(--text-dim)] mb-2 uppercase tracking-[0.15em]">{title}</h3>
  )
}

// Escalation form
function EscalationForm() {
  const { escalationTarget, submitEscalation, cancelEscalation } = useDashboard()
  const [selectedDept, setSelectedDept] = useState<number | null>(null)
  const [selectedPerson, setSelectedPerson] = useState<string | null>(null)

  if (!escalationTarget) return null

  const dept = selectedDept !== null ? DEPARTMENTS[selectedDept] : null

  return (
    <>
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] font-medium text-[var(--accent)] uppercase tracking-[0.15em]">
          Escalate Event
        </span>
        <button onClick={cancelEscalation} className="text-[var(--text-dim)] hover:text-[var(--text-muted)]">
          <X size={12} />
        </button>
      </div>

      {/* Event being escalated */}
      <div className="mb-4 p-2 border border-[var(--accent-dim)] bg-[var(--accent-dim)]">
        <div className="flex items-center gap-1.5 mb-1">
          <AlertTriangle size={10} className="text-[var(--accent)]" />
          <span className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-wider">
            {escalationTarget.eventType.replace(/_/g, ' ')}
          </span>
        </div>
        <p className="text-[10px] text-[var(--text-secondary)] leading-[1.4] line-clamp-2">
          {escalationTarget.description}
        </p>
      </div>

      {/* Department selection */}
      <div className="mb-3">
        <SectionHeader title="Department" />
        <div className="space-y-[1px]">
          {DEPARTMENTS.map((dept, i) => (
            <button
              key={dept.name}
              onClick={() => { setSelectedDept(i); setSelectedPerson(null) }}
              className={`flex items-center justify-between w-full px-2 py-1.5 text-[10px] font-mono uppercase tracking-wider transition-all ${
                selectedDept === i
                  ? 'text-[var(--text-primary)] bg-white/[0.04] border border-[var(--border-active)]'
                  : 'text-[var(--text-dim)] hover:text-[var(--text-muted)] border border-transparent'
              }`}
            >
              {dept.name}
              <ChevronDown size={8} className={selectedDept === i ? 'rotate-180' : ''} />
            </button>
          ))}
        </div>
      </div>

      {/* Person selection — shown when department selected */}
      {dept && (
        <div className="mb-4 animate-fadeUp">
          <SectionHeader title="Recipient" />
          <div className="space-y-[1px]">
            {dept.members.map(person => (
              <button
                key={person}
                onClick={() => setSelectedPerson(person)}
                className={`flex items-center w-full px-2 py-1.5 text-[10px] font-mono tracking-wider transition-all ${
                  selectedPerson === person
                    ? 'text-[var(--text-primary)] bg-white/[0.04] border border-[var(--border-active)]'
                    : 'text-[var(--text-dim)] hover:text-[var(--text-muted)] border border-transparent'
                }`}
              >
                {person}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Submit */}
      <button
        onClick={() => {
          if (dept && selectedPerson) {
            submitEscalation(dept.name, selectedPerson)
          }
        }}
        disabled={!dept || !selectedPerson}
        className="flex items-center gap-1.5 w-full px-3 py-2 text-[10px] font-mono uppercase tracking-wider text-[var(--accent)] border border-[var(--accent-dim)] hover:bg-[var(--accent-dim)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        <Send size={10} /> Submit Escalation
      </button>
    </>
  )
}

// Default intelligence brief view
function BriefView() {
  const { brief, loading } = useBriefs()

  if (loading) {
    return (
      <div className="space-y-2.5">
        <div className="h-2.5 bg-white/[0.02] animate-pulse w-3/4" />
        <div className="h-2.5 bg-white/[0.02] animate-pulse w-full" />
        <div className="h-2.5 bg-white/[0.02] animate-pulse w-5/6" />
      </div>
    )
  }

  if (!brief) {
    return (
      <p className="text-[11px] text-[var(--text-dim)] font-mono">
        Awaiting correlation engine...
      </p>
    )
  }

  const style = brief.threat_level
    ? threatStyles[brief.threat_level]
    : { text: 'text-[var(--text-dim)]', dot: 'bg-[var(--text-dim)]' }

  return (
    <>
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2.5">
          {brief.threat_level && (
            <div className="flex items-center gap-1.5">
              <div className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
              <span className={`text-[10px] font-mono uppercase tracking-wider ${style.text}`}>
                {brief.threat_level}
              </span>
            </div>
          )}
          {brief.confidence !== null && (
            <span className="text-[10px] font-mono text-[var(--text-dim)] tabular-nums">
              {brief.confidence}%
            </span>
          )}
        </div>
        <p className="text-[12px] text-[var(--text-secondary)] leading-[1.5]">{brief.summary}</p>
      </div>

      <div className="mb-4">
        <SectionHeader title="Evidence" />
        {brief.evidence_chain && brief.evidence_chain.length > 0 ? (
          <ul className="space-y-1.5">
            {brief.evidence_chain.map((item, idx) => (
              <li key={idx} className="flex gap-2 text-[11px] text-[var(--text-secondary)] leading-[1.5]">
                <span className="text-[var(--text-dim)] shrink-0">&mdash;</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-[11px] text-[var(--text-dim)] font-mono">None available</p>
        )}
      </div>

      <div className="mb-4">
        <SectionHeader title="Timeline" />
        {brief.timeline ? (
          <div className="text-[11px] text-[var(--text-secondary)] leading-[1.5] whitespace-pre-line">
            {brief.timeline}
          </div>
        ) : (
          <p className="text-[11px] text-[var(--text-dim)] font-mono">None available</p>
        )}
      </div>

      <div className="mb-4">
        <SectionHeader title="Priorities" />
        {brief.collection_priorities && brief.collection_priorities.length > 0 ? (
          <ul className="space-y-1.5">
            {brief.collection_priorities.map((item, idx) => (
              <li key={idx} className="flex gap-2 text-[11px] text-[var(--text-secondary)] leading-[1.5]">
                <span className="text-[var(--text-dim)] shrink-0">&mdash;</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-[11px] text-[var(--text-dim)] font-mono">None available</p>
        )}
      </div>

      {brief.information_gaps && brief.information_gaps.length > 0 && (
        <div className="mb-4">
          <SectionHeader title="Gaps" />
          <ul className="space-y-1.5">
            {brief.information_gaps.map((item, idx) => (
              <li key={idx} className="flex gap-2 text-[11px] text-[var(--text-dim)] leading-[1.5]">
                <span className="shrink-0">?</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-5 pt-3 border-t border-[var(--border-subtle)]">
        <p className="text-[10px] text-[var(--text-dim)] font-mono tabular-nums">
          {formatRelativeTime(brief.generated_at)}
        </p>
      </div>
    </>
  )
}

// Selected movement event detail view
function EventDetailView({ event }: { event: MovementEvent }) {
  const { escalatedIds, startEscalation, clearSelection } = useDashboard()
  const isEscalated = escalatedIds.has(event.id)
  const isHighThreat = event.event_type === 'speed_anomaly' || event.event_type === 'zone_entry'

  return (
    <>
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] font-medium text-[var(--text-dim)] uppercase tracking-[0.15em]">
          Event Detail
        </span>
        <button onClick={clearSelection} className="text-[var(--text-dim)] hover:text-[var(--text-muted)]">
          <X size={12} />
        </button>
      </div>

      <div className="mb-3">
        <div className="flex items-center gap-2 mb-2">
          <div className={`w-2 h-2 rounded-full ${isHighThreat ? 'bg-[var(--accent)]' : 'bg-[var(--text-muted)]'}`} />
          <span className={`text-[11px] font-mono uppercase tracking-wider ${isHighThreat ? 'text-[var(--accent)]' : 'text-[var(--text-primary)]'}`}>
            {event.event_type.replace(/_/g, ' ')}
          </span>
        </div>
        <p className="text-[12px] text-[var(--text-secondary)] leading-[1.5]">
          {event.description}
        </p>
      </div>

      <div className="mb-4 space-y-1.5">
        <SectionHeader title="Details" />
        <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--text-dim)] tabular-nums">
          <span>Vessel</span>
          <span className="text-[var(--text-secondary)]">{event.vessel_mmsi}</span>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--text-dim)] tabular-nums">
          <span>Location</span>
          <span className="text-[var(--text-secondary)]">{event.location_lat.toFixed(3)}°N {event.location_lon.toFixed(3)}°E</span>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--text-dim)] tabular-nums">
          <span>Time</span>
          <span className="text-[var(--text-secondary)]">{formatTime(event.detected_at)}</span>
        </div>
      </div>

      <div className="mb-4">
        <SectionHeader title="Narrative Assessment" />
        <p className="text-[11px] text-[var(--text-secondary)] leading-[1.5]">
          {isHighThreat
            ? 'This event has been flagged as potentially threatening. The vessel behavior pattern suggests coordination with other recent activity in the region.'
            : 'This event is within normal operating parameters but is being tracked as part of ongoing regional monitoring.'}
        </p>
      </div>

      {!isEscalated ? (
        <button
          onClick={() => startEscalation({
            eventId: event.id,
            eventType: event.event_type,
            description: event.description,
          })}
          className="flex items-center gap-1.5 w-full px-3 py-2 text-[10px] font-mono uppercase tracking-wider text-[var(--accent)] border border-[var(--accent-dim)] hover:bg-[var(--accent-dim)] transition-colors"
        >
          <AlertTriangle size={10} /> Escalate to Command
        </button>
      ) : (
        <div className="flex items-center gap-1.5 px-3 py-2 text-[10px] font-mono text-[var(--accent)] uppercase tracking-wider border border-[var(--accent-dim)] bg-[var(--accent-dim)]">
          <AlertTriangle size={10} /> Escalated
        </div>
      )}
    </>
  )
}

// Cluster summary view
function ClusterView() {
  const { focusCluster, setFocusCluster, escalatedIds, startEscalation } = useDashboard()
  if (!focusCluster) return null

  const isHighThreat = focusCluster.type === 'speed_anomaly' || focusCluster.type === 'zone_entry'
  const allEscalated = focusCluster.points.every(p => escalatedIds.has(p.id))

  return (
    <>
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] font-medium text-[var(--text-dim)] uppercase tracking-[0.15em]">
          Cluster Analysis
        </span>
        <button onClick={() => setFocusCluster(null)} className="text-[var(--text-dim)] hover:text-[var(--text-muted)]">
          <X size={12} />
        </button>
      </div>

      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <div className={`w-2 h-2 rounded-full ${isHighThreat ? 'bg-[var(--accent)]' : 'bg-[var(--text-muted)]'}`} />
          <span className={`text-[12px] font-mono uppercase tracking-wider ${isHighThreat ? 'text-[var(--accent)]' : 'text-[var(--text-primary)]'}`}>
            {focusCluster.type.replace(/_/g, ' ')}
          </span>
        </div>
        <p className="text-[12px] text-[var(--text-secondary)] leading-[1.5]">
          {focusCluster.points.length} coordinated events detected within this cluster.
        </p>
      </div>

      <div className="mb-4">
        <SectionHeader title="Cluster Details" />
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--text-dim)]">
            <span>Events</span>
            <span className="text-[var(--text-secondary)] tabular-nums">{focusCluster.points.length}</span>
          </div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--text-dim)]">
            <span>Time span</span>
            <span className="text-[var(--text-secondary)] tabular-nums">
              {formatTime(focusCluster.startTime)} — {formatTime(focusCluster.endTime)}
            </span>
          </div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--text-dim)]">
            <span>Vessels</span>
            <span className="text-[var(--text-secondary)] tabular-nums">
              {new Set(focusCluster.points.map(p => p.vessel_mmsi)).size}
            </span>
          </div>
        </div>
      </div>

      <div className="mb-4">
        <SectionHeader title="Event Sequence" />
        <div className="space-y-1">
          {focusCluster.points.map((point, idx) => (
            <div key={point.id} className="flex items-start gap-2">
              <div className="flex flex-col items-center shrink-0 mt-0.5">
                <div className={`w-1.5 h-1.5 rounded-full ${escalatedIds.has(point.id) ? 'bg-[var(--accent)]' : 'bg-[var(--text-dim)]'}`} />
                {idx < focusCluster.points.length - 1 && (
                  <div className="w-px h-3 bg-[var(--border-subtle)]" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 text-[10px] font-mono tabular-nums">
                  <span className="text-[var(--text-dim)]">{formatTime(point.detected_at)}</span>
                  <span className="text-[var(--text-secondary)] truncate">{point.vessel_mmsi}</span>
                  {escalatedIds.has(point.id) && (
                    <AlertTriangle size={8} className="text-[var(--accent)] shrink-0" />
                  )}
                </div>
                {point.description && (
                  <p className="text-[10px] text-[var(--text-dim)] leading-[1.4] truncate">
                    {point.description}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-4">
        <SectionHeader title="Assessment" />
        <p className="text-[11px] text-[var(--text-secondary)] leading-[1.5]">
          {isHighThreat
            ? `This cluster of ${focusCluster.points.length} events suggests coordinated activity that warrants immediate attention.`
            : `A cluster of ${focusCluster.points.length} related events has been detected. The pattern should be monitored for escalation.`}
        </p>
      </div>

      {!allEscalated ? (
        <button
          onClick={() => startEscalation({
            eventId: focusCluster.id,
            eventType: focusCluster.type,
            description: `Cluster of ${focusCluster.points.length} ${focusCluster.type.replace(/_/g, ' ')} events`,
          })}
          className="flex items-center gap-1.5 w-full px-3 py-2 text-[10px] font-mono uppercase tracking-wider text-[var(--accent)] border border-[var(--accent-dim)] hover:bg-[var(--accent-dim)] transition-colors"
        >
          <AlertTriangle size={10} /> Escalate Cluster
        </button>
      ) : (
        <div className="flex items-center gap-1.5 px-3 py-2 text-[10px] font-mono text-[var(--accent)] uppercase tracking-wider border border-[var(--accent-dim)] bg-[var(--accent-dim)]">
          <AlertTriangle size={10} /> Cluster Escalated
        </div>
      )}
    </>
  )
}

export function BriefPanel() {
  const { selectedMovementEventId, focusCluster, escalationTarget } = useDashboard()
  const { movementEvents } = useMovementEvents()

  const selectedEvent = selectedMovementEventId
    ? movementEvents.find(e => e.id === selectedMovementEventId) || null
    : null

  // Priority: Escalation > Individual event > Cluster > Brief
  const showEscalation = !!escalationTarget
  const showEventDetail = !showEscalation && !!selectedEvent
  const showCluster = !showEscalation && !showEventDetail && !!focusCluster
  const showBrief = !showEscalation && !showEventDetail && !showCluster

  return (
    <div className="h-full overflow-y-auto bg-[var(--bg-panel)] px-4 py-3">
      {/* Header with breadcrumb */}
      <div className="mb-4 pb-3 border-b border-[var(--border-subtle)]">
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-[var(--text-dim)] uppercase tracking-wider">
          <span className={showBrief ? 'text-[var(--text-primary)]' : ''}>Brief</span>
          {(showCluster || (showEventDetail && focusCluster)) && (
            <>
              <ChevronRight size={8} />
              <span className={showCluster ? 'text-[var(--text-primary)]' : ''}>Cluster</span>
            </>
          )}
          {showEventDetail && (
            <>
              <ChevronRight size={8} />
              <span className="text-[var(--text-primary)]">Event</span>
            </>
          )}
          {showEscalation && (
            <>
              <ChevronRight size={8} />
              <span className="text-[var(--accent)]">Escalate</span>
            </>
          )}
        </div>
      </div>

      {showEscalation && <EscalationForm />}
      {showCluster && <ClusterView />}
      {showEventDetail && selectedEvent && <EventDetailView event={selectedEvent} />}
      {showBrief && <BriefView />}
    </div>
  )
}
