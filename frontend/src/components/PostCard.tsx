import type { SocialPost, MovementEvent } from '../types/database'

interface PostCardProps {
  post: SocialPost
  movementEvent?: MovementEvent | null
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

// Format view count with K/M suffixes
function formatViews(views: number | null): string {
  if (views === null) return '0'
  if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`
  if (views >= 1000) return `${(views / 1000).toFixed(1)}K`
  return views.toString()
}

// Get category badge styling
function getCategoryStyle(eventType: string): { bg: string; text: string } {
  switch (eventType.toLowerCase()) {
    case 'convoy':
      return { bg: 'bg-orange-100', text: 'text-orange-700' }
    case 'naval':
      return { bg: 'bg-blue-100', text: 'text-blue-700' }
    case 'flight':
      return { bg: 'bg-sky-100', text: 'text-sky-700' }
    case 'restricted_zone':
      return { bg: 'bg-red-100', text: 'text-red-700' }
    default:
      return { bg: 'bg-slate-100', text: 'text-slate-600' }
  }
}

// Get border color based on movement event category
function getBorderColor(eventType?: string): string {
  if (!eventType) return 'border-blue-500'
  switch (eventType.toLowerCase()) {
    case 'convoy':
      return 'border-orange-500'
    case 'naval':
      return 'border-blue-600'
    case 'flight':
      return 'border-sky-500'
    case 'restricted_zone':
      return 'border-red-500'
    default:
      return 'border-blue-500'
  }
}

export function PostCard({ post, movementEvent }: PostCardProps) {
  const borderColor = getBorderColor(movementEvent?.event_type)

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border-l-4 ${borderColor} p-3 mb-2 animate-fadeIn`}
    >
      {/* Channel badge */}
      <div className="mb-2">
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
          {post.channel}
        </span>
      </div>

      {/* Text excerpt */}
      <p className="text-sm text-gray-800 line-clamp-2 mb-2">
        {post.text}
      </p>

      {/* Movement event category tag */}
      {movementEvent && (
        <div className="mb-2">
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium uppercase ${
              getCategoryStyle(movementEvent.event_type).bg
            } ${getCategoryStyle(movementEvent.event_type).text}`}
          >
            {movementEvent.event_type}
          </span>
        </div>
      )}

      {/* Location tag (if movement event has coordinates) */}
      {movementEvent && movementEvent.location_lat && movementEvent.location_lon && (
        <div className="text-xs text-gray-500 mb-2">
          {movementEvent.location_lat.toFixed(1)}°N, {movementEvent.location_lon.toFixed(1)}°E
        </div>
      )}

      {/* Views and time */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>{formatViews(post.views)} views</span>
        <span>{timeAgo(post.timestamp)}</span>
      </div>
    </div>
  )
}
