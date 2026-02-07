import { useBriefs } from '../hooks/useBriefs'
import { ThreatLevel } from '../types/database'

const threatLevelStyles: Record<ThreatLevel, { bg: string; text: string }> = {
  GREEN: { bg: 'bg-green-100', text: 'text-green-800' },
  AMBER: { bg: 'bg-amber-100', text: 'text-amber-800' },
  RED: { bg: 'bg-red-100', text: 'text-red-800' },
}

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

export function BriefPanel() {
  const { brief, loading } = useBriefs()

  if (loading) {
    return (
      <div className="h-full overflow-y-auto bg-white px-4 py-3">
        <div className="mb-4 pb-3 border-b border-slate-200">
          <h2 className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
            Intelligence Brief
          </h2>
        </div>
        <div className="space-y-2">
          <div className="h-4 bg-slate-200 rounded animate-pulse w-3/4" />
          <div className="h-4 bg-slate-200 rounded animate-pulse w-full" />
          <div className="h-4 bg-slate-200 rounded animate-pulse w-5/6" />
        </div>
      </div>
    )
  }

  if (!brief) {
    return (
      <div className="h-full overflow-y-auto bg-white px-4 py-3">
        <div className="mb-4 pb-3 border-b border-slate-200">
          <h2 className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
            Intelligence Brief
          </h2>
        </div>
        <p className="text-sm text-slate-400">
          No intelligence brief generated yet. Awaiting correlation engine output.
        </p>
      </div>
    )
  }

  const threatStyle = brief.threat_level
    ? threatLevelStyles[brief.threat_level]
    : { bg: 'bg-slate-100', text: 'text-slate-700' }

  return (
    <div className="h-full overflow-y-auto bg-white px-4 py-3">
      {/* Header */}
      <div className="mb-4 pb-3 border-b border-slate-200">
        <h2 className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
          Intelligence Brief
        </h2>
      </div>

      {/* Assessment Section */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          {brief.threat_level && (
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${threatStyle.bg} ${threatStyle.text}`}
            >
              {brief.threat_level}
            </span>
          )}
          {brief.confidence !== null && (
            <span className="text-xs text-slate-500">{brief.confidence}% confidence</span>
          )}
        </div>
        <p className="text-sm text-slate-700 leading-relaxed">{brief.summary}</p>
      </div>

      {/* Evidence Chain Section */}
      <div className="mb-6">
        <h3 className="text-xs font-semibold text-slate-700 mb-2">Evidence</h3>
        {brief.evidence_chain && brief.evidence_chain.length > 0 ? (
          <ul className="space-y-1.5 list-disc list-inside text-sm text-slate-600">
            {brief.evidence_chain.map((item, idx) => (
              <li key={idx} className="leading-relaxed">
                {item}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-400">No evidence chain available</p>
        )}
      </div>

      {/* Timeline Section */}
      <div className="mb-6">
        <h3 className="text-xs font-semibold text-slate-700 mb-2">Timeline</h3>
        {brief.timeline ? (
          <div className="text-sm text-slate-600 leading-relaxed whitespace-pre-line">
            {brief.timeline}
          </div>
        ) : (
          <p className="text-sm text-slate-400">No timeline available</p>
        )}
      </div>

      {/* Collection Priorities Section */}
      <div className="mb-6">
        <h3 className="text-xs font-semibold text-slate-700 mb-2">Collection Priorities</h3>
        {brief.collection_priorities && brief.collection_priorities.length > 0 ? (
          <ul className="space-y-1.5 list-disc list-inside text-sm text-slate-600">
            {brief.collection_priorities.map((item, idx) => (
              <li key={idx} className="leading-relaxed">
                {item}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-400">No collection priorities</p>
        )}
      </div>

      {/* Information Gaps Section */}
      {brief.information_gaps && brief.information_gaps.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-slate-500 italic mb-2">Information Gaps</h3>
          <ul className="space-y-1.5 list-disc list-inside text-sm text-slate-500 italic">
            {brief.information_gaps.map((item, idx) => (
              <li key={idx} className="leading-relaxed">
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Generated Time Footer */}
      <div className="mt-8 pt-4 border-t border-slate-100">
        <p className="text-xs text-slate-400">Generated {formatRelativeTime(brief.generated_at)}</p>
      </div>
    </div>
  )
}
