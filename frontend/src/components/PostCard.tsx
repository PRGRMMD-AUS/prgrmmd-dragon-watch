import { AlertTriangle, Filter } from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import type { SocialPost, MovementEvent } from '../types/database'

interface PostCardProps {
  post: SocialPost
  movementEvent?: MovementEvent | null
  isSelected?: boolean
  onSelect?: () => void
}

function timeAgo(dateString: string): string {
  const now = new Date()
  const date = new Date(dateString)
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h`
  return `${Math.floor(hours / 24)}d`
}

function formatViews(views: number | null): string {
  if (views === null) return '0'
  if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`
  if (views >= 1000) return `${(views / 1000).toFixed(1)}K`
  return views.toString()
}

function isHighSeverity(eventType?: string): boolean {
  if (!eventType) return false
  return eventType.toLowerCase() === 'restricted_zone' || eventType.toLowerCase() === 'speed_anomaly'
}

export function PostCard({ post, movementEvent, isSelected = false, onSelect }: PostCardProps) {
  const { escalatedIds, escalateEvent, narrativeFilter, setNarrativeFilter } = useDashboard()
  const high = isHighSeverity(movementEvent?.event_type)
  const borderColor = high
    ? 'border-l-[var(--accent)]'
    : movementEvent
      ? 'border-l-[var(--threat-med)]'
      : 'border-l-[var(--border-glass)]'

  const isEscalated = escalatedIds.has(post.id) || (movementEvent && escalatedIds.has(movementEvent.id))
  const isFiltered = narrativeFilter === movementEvent?.event_type

  return (
    <div
      onClick={onSelect}
      className={`bg-[var(--bg-card)] border border-[var(--border-subtle)] border-l-2 ${borderColor} p-3 cursor-pointer hover:bg-[var(--bg-card-hover)] transition-colors duration-150 animate-fadeUp ${isSelected ? 'card-selected' : ''}`}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-[10px] font-mono text-[var(--text-dim)] uppercase tracking-wider">
          {post.channel}
        </span>
        {movementEvent && (
          <>
            <span className="text-[var(--text-dim)]">/</span>
            <span className={`text-[10px] font-mono uppercase tracking-wider ${high ? 'text-[var(--accent)]' : 'text-[var(--text-muted)]'}`}>
              {movementEvent.event_type.replace(/_/g, ' ')}
            </span>
          </>
        )}
        {(high || isEscalated) && (
          <div className={`w-1.5 h-1.5 rounded-full ml-auto shrink-0 ${isEscalated ? 'bg-[var(--accent)]' : 'bg-[var(--accent)]'}`} />
        )}
      </div>

      <p className="text-[12px] text-[var(--text-secondary)] line-clamp-2 leading-[1.4] mb-1.5">
        {post.text}
      </p>

      <div className="flex items-center gap-3 text-[10px] font-mono text-[var(--text-dim)] tabular-nums">
        {movementEvent?.location_lat && movementEvent?.location_lon && (
          <span>{movementEvent.location_lat.toFixed(1)}°N {movementEvent.location_lon.toFixed(1)}°E</span>
        )}
        <span>{formatViews(post.views)} views</span>
        <span className="ml-auto">{timeAgo(post.timestamp)}</span>
      </div>

      {/* Actions — visible when selected */}
      {isSelected && (
        <div className="flex items-center gap-2 mt-2">
          {/* Filter narrative on map */}
          {movementEvent && (
            <button
              onClick={(e) => { e.stopPropagation(); setNarrativeFilter(movementEvent.event_type) }}
              className={`flex items-center gap-1 px-2 py-1 text-[10px] font-mono uppercase tracking-wider border transition-colors ${
                isFiltered
                  ? 'text-[var(--text-primary)] border-[var(--border-active)] bg-white/[0.03]'
                  : 'text-[var(--text-muted)] border-[var(--border-subtle)] hover:text-[var(--text-primary)] hover:border-[var(--border-glass)]'
              }`}
            >
              <Filter size={9} /> {isFiltered ? 'Filtered' : 'Filter Map'}
            </button>
          )}

          {/* Escalate */}
          {!isEscalated ? (
            <button
              onClick={(e) => { e.stopPropagation(); escalateEvent(movementEvent?.id || post.id) }}
              className="flex items-center gap-1 px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-[var(--accent)] border border-[var(--accent-dim)] hover:bg-[var(--accent-dim)] transition-colors"
            >
              <AlertTriangle size={9} /> Escalate
            </button>
          ) : (
            <div className="flex items-center gap-1 text-[10px] font-mono text-[var(--accent)] uppercase tracking-wider">
              <AlertTriangle size={9} /> Escalated
            </div>
          )}
        </div>
      )}
    </div>
  )
}
