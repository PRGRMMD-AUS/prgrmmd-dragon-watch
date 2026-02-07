import type { Article } from '../types/database'

interface ArticleCardProps {
  article: Article
  isCoordinated?: boolean
}

// Helper to format relative time
function timeAgo(dateString: string): string {
  const now = new Date()
  const date = new Date(dateString)
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

// Get border color based on tone score
function getBorderColor(toneScore: number | null): string {
  if (toneScore === null) return 'border-slate-300'
  if (toneScore < -5) return 'border-red-500'
  if (toneScore < -2) return 'border-amber-500'
  return 'border-green-500'
}

export function ArticleCard({ article, isCoordinated = false }: ArticleCardProps) {
  const borderColor = isCoordinated ? 'border-purple-500' : getBorderColor(article.tone_score)

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border-l-4 ${borderColor} p-3 mb-2 animate-fadeIn`}
    >
      {/* Title */}
      <h3 className="font-semibold text-sm text-slate-900 line-clamp-2 mb-2">
        {article.title}
      </h3>

      {/* Domain and Coordinated badge */}
      <div className="flex items-center gap-2 mb-2">
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">
          {article.domain}
        </span>
        {isCoordinated && (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-700 uppercase">
            Coordinated
          </span>
        )}
      </div>

      {/* Tone score and time */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>
          Tone: {article.tone_score !== null ? article.tone_score.toFixed(1) : 'N/A'}
        </span>
        <span>{timeAgo(article.published_at)}</span>
      </div>
    </div>
  )
}
