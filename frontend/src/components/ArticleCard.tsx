import { AlertTriangle } from 'lucide-react'
import { useDashboard } from '../context/DashboardContext'
import type { Article } from '../types/database'

interface ArticleCardProps {
  article: Article
  isCoordinated?: boolean
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

function getSeverity(toneScore: number | null): 'high' | 'med' | 'low' {
  if (toneScore === null) return 'low'
  if (toneScore < -5) return 'high'
  if (toneScore < -2) return 'med'
  return 'low'
}

export function ArticleCard({ article, isCoordinated = false, isSelected = false, onSelect }: ArticleCardProps) {
  const { escalatedIds, escalateEvent } = useDashboard()
  const severity = isCoordinated ? 'high' : getSeverity(article.tone_score)
  const borderColor = severity === 'high'
    ? 'border-l-[var(--accent)]'
    : severity === 'med'
      ? 'border-l-[var(--threat-med)]'
      : 'border-l-[var(--border-glass)]'

  const isEscalated = escalatedIds.has(article.id)

  return (
    <div
      onClick={onSelect}
      className={`bg-[var(--bg-card)] border border-[var(--border-subtle)] border-l-2 ${borderColor} p-3 cursor-pointer hover:bg-[var(--bg-card-hover)] transition-colors duration-150 animate-fadeUp ${isSelected ? 'card-selected' : ''}`}
    >
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <h3 className="font-medium text-[12px] text-[var(--text-primary)] line-clamp-2 leading-[1.4]">
          {article.title}
        </h3>
        {(severity === 'high' || isEscalated) && (
          <div className={`w-1.5 h-1.5 rounded-full shrink-0 mt-1 ${isEscalated ? 'bg-[var(--accent)]' : 'bg-[var(--accent)]'}`} />
        )}
      </div>

      <div className="flex items-center gap-2">
        <span className="text-[10px] font-mono text-[var(--text-dim)] uppercase tracking-wider">
          {article.domain}
        </span>
        {isCoordinated && (
          <span className="text-[10px] font-mono text-[var(--accent)] uppercase tracking-wider">
            coordinated
          </span>
        )}
        <span className="ml-auto text-[10px] font-mono text-[var(--text-dim)] tabular-nums">
          {timeAgo(article.published_at)}
        </span>
      </div>

      {/* Escalate action — visible when selected */}
      {isSelected && !isEscalated && (
        <button
          onClick={(e) => { e.stopPropagation(); escalateEvent(article.id) }}
          className="flex items-center gap-1 mt-2 px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-[var(--accent)] border border-[var(--accent-dim)] hover:bg-[var(--accent-dim)] transition-colors"
        >
          <AlertTriangle size={9} /> Escalate
        </button>
      )}
      {isSelected && isEscalated && (
        <div className="flex items-center gap-1 mt-2 text-[10px] font-mono text-[var(--accent)] uppercase tracking-wider">
          <AlertTriangle size={9} /> Escalated
        </div>
      )}
    </div>
  )
}
