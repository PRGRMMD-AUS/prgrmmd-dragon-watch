import { useMemo, useEffect, useRef, useState } from 'react'
import { useArticles } from '../hooks/useArticles'
import { useSocialPosts } from '../hooks/useSocialPosts'
import { useNarrativeEvents } from '../hooks/useNarrativeEvents'
import { useMovementEvents } from '../hooks/useMovementEvents'
import { useMovementHeatmap } from '../hooks/useMovementHeatmap'
import { useDashboard } from '../context/DashboardContext'
import { ArticleCard } from './ArticleCard'
import { PostCard } from './PostCard'
import type { Article, SocialPost, MovementEvent } from '../types/database'
import type { FeedFilter } from '../context/DashboardContext'
import type { Cluster, HeatmapPoint } from '../hooks/useMovementHeatmap'
import { Layers, AlertTriangle, List, Anchor } from 'lucide-react'

const EVENT_TYPE_COLORS: Record<string, string> = {
  speed_anomaly: '#ef4444',
  formation_change: '#a78bfa',
  zone_entry: '#f97316',
  course_deviation: '#38bdf8',
}

function formatEventTime(detected_at: string): string {
  const d = new Date(detected_at)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

/** Lightweight card for a cluster movement event point */
function ClusterEventCard({ point, isSelected, onSelect }: { point: HeatmapPoint; isSelected: boolean; onSelect: () => void }) {
  const color = EVENT_TYPE_COLORS[point.type] || '#6b7280'
  return (
    <button
      onClick={onSelect}
      className={`w-full text-left px-2.5 py-2 transition-all duration-150 ${
        isSelected
          ? 'bg-white/[0.05] border border-[var(--border-active)]'
          : 'bg-white/[0.01] border border-transparent hover:bg-white/[0.03]'
      }`}
    >
      <div className="flex items-center gap-2 mb-0.5">
        <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: color }} />
        <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase tracking-wider">
          {point.type.replace(/_/g, ' ')}
        </span>
        <span className="text-[9px] font-mono text-[var(--text-dim)] tabular-nums ml-auto">
          {formatEventTime(point.detected_at)}
        </span>
      </div>
      {point.description && (
        <p className="text-[10px] text-[var(--text-secondary)] leading-[1.4] line-clamp-2 ml-3.5">
          {point.description}
        </p>
      )}
      <div className="flex items-center gap-2 mt-0.5 ml-3.5">
        <Anchor size={8} className="text-[var(--text-dim)]" />
        <span className="text-[9px] font-mono text-[var(--text-dim)] tabular-nums">{point.vessel_mmsi}</span>
        <span className="text-[9px] font-mono text-[var(--text-dim)] tabular-nums">{point.lat.toFixed(2)}°N {point.lon.toFixed(2)}°E</span>
      </div>
    </button>
  )
}

type FeedItem =
  | { type: 'article'; data: Article; sortTime: string }
  | { type: 'post'; data: SocialPost; sortTime: string; matchedEvent: MovementEvent | null }

function findMatchingMovementEvent(
  postTimestamp: string,
  movementEvents: MovementEvent[]
): MovementEvent | null {
  const postTime = new Date(postTimestamp).getTime()
  const fiveMinutes = 5 * 60 * 1000
  let closest: MovementEvent | null = null
  let closestDiff = Infinity

  for (const event of movementEvents) {
    const eventTime = new Date(event.detected_at).getTime()
    const diff = Math.abs(eventTime - postTime)
    if (diff <= fiveMinutes && diff < closestDiff) {
      closest = event
      closestDiff = diff
    }
  }
  return closest
}

const FILTER_OPTIONS: { key: FeedFilter; label: string; icon: typeof List }[] = [
  { key: 'all', label: 'All', icon: List },
  { key: 'clusters', label: 'Clusters', icon: Layers },
  { key: 'high-threat', label: 'High', icon: AlertTriangle },
]

export function EventFeed() {
  const { articles, loading: articlesLoading } = useArticles()
  const { posts, loading: postsLoading } = useSocialPosts()
  const { coordinatedArticleIds, loading: narrativeLoading } = useNarrativeEvents()
  const { movementEvents, loading: movementLoading } = useMovementEvents()
  const { pointClusterMap, clusters } = useMovementHeatmap()
  const {
    selectedId,
    selectedMovementEventId,
    selectCard,
    selectFromMap,
    clearSelection,
    feedFilter,
    setFeedFilter,
    focusCluster,
    setFocusCluster,
    narrativeFilter,
    setNarrativeFilter,
  } = useDashboard()

  // Track which sub-category is selected within Clusters view
  const [clusterSubCategory, setClusterSubCategory] = useState<string | null>(null)

  const cardRefs = useRef<Record<string, HTMLDivElement | null>>({})

  // Reset sub-category when leaving clusters tab
  const handleSetFilter = (key: FeedFilter) => {
    if (key !== 'clusters') {
      setClusterSubCategory(null)
      setNarrativeFilter(null)
    }
    setFeedFilter(key)
  }

  const feedItems = useMemo<FeedItem[]>(() => {
    const items: FeedItem[] = []

    articles.forEach((article) => {
      items.push({ type: 'article', data: article, sortTime: article.published_at })
    })

    posts.forEach((post) => {
      const matchedEvent = findMatchingMovementEvent(post.timestamp, movementEvents)
      items.push({ type: 'post', data: post, sortTime: post.timestamp, matchedEvent })
    })

    items.sort((a, b) => new Date(b.sortTime).getTime() - new Date(a.sortTime).getTime())
    return items
  }, [articles, posts, movementEvents])

  // Build movement event ID -> post ID mapping
  const movementToPostId = useMemo(() => {
    const map: Record<string, string> = {}
    for (const item of feedItems) {
      if (item.type === 'post' && item.matchedEvent) {
        map[item.matchedEvent.id] = item.data.id
      }
    }
    return map
  }, [feedItems])

  // High threat: articles with tone_score < -5 or coordinated, posts matched to speed_anomaly/zone_entry
  const highThreatIds = useMemo(() => {
    const ids = new Set<string>()
    for (const item of feedItems) {
      if (item.type === 'article') {
        if (coordinatedArticleIds.has(item.data.id) || (item.data.tone_score !== null && item.data.tone_score < -5)) {
          ids.add(item.data.id)
        }
      } else {
        if (item.matchedEvent && (item.matchedEvent.event_type === 'speed_anomaly' || item.matchedEvent.event_type === 'zone_entry')) {
          ids.add(item.data.id)
        }
      }
    }
    return ids
  }, [feedItems, coordinatedArticleIds])

  // Apply feed filter for flat views (All, High)
  const filteredItems = useMemo(() => {
    switch (feedFilter) {
      case 'high-threat':
        return feedItems.filter(item => highThreatIds.has(item.data.id))
      default:
        return feedItems
    }
  }, [feedItems, feedFilter, highThreatIds])

  // Filter counts
  const counts = useMemo(() => ({
    all: feedItems.length,
    clusters: clusters.length,
    'high-threat': highThreatIds.size,
  }), [feedItems.length, clusters.length, highThreatIds.size])

  // Cluster sub-categories: group clusters by event type
  const clustersByType = useMemo(() => {
    const grouped: Record<string, Cluster[]> = {}
    for (const cluster of clusters) {
      if (!grouped[cluster.type]) grouped[cluster.type] = []
      grouped[cluster.type].push(cluster)
    }
    return grouped
  }, [clusters])

  // Get clusters + their feed items for the selected sub-category
  const subCategoryClusters = useMemo(() => {
    if (!clusterSubCategory) return null

    const typeClusters = clustersByType[clusterSubCategory] || []

    // Build cluster ID → matched feed items
    const clusterItemMap = new Map<string, FeedItem[]>()
    for (const item of feedItems) {
      if (item.type !== 'post' || !item.matchedEvent) continue
      const clusterId = pointClusterMap[item.matchedEvent.id]
      if (!clusterId) continue
      if (!clusterItemMap.has(clusterId)) clusterItemMap.set(clusterId, [])
      clusterItemMap.get(clusterId)!.push(item)
    }

    return typeClusters.map(cluster => ({
      cluster,
      items: clusterItemMap.get(cluster.id) || [],
    }))
  }, [clusterSubCategory, clustersByType, feedItems, pointClusterMap])

  // Scroll to card when map selects a movement event
  useEffect(() => {
    if (!selectedMovementEventId) return
    const postId = movementToPostId[selectedMovementEventId]
    if (postId && cardRefs.current[postId]) {
      cardRefs.current[postId]?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [selectedMovementEventId, movementToPostId])

  // Scroll to card when selectedId changes from any source
  useEffect(() => {
    if (!selectedId) return
    if (cardRefs.current[selectedId]) {
      cardRefs.current[selectedId]?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [selectedId])

  const loading = articlesLoading || postsLoading || narrativeLoading || movementLoading

  // Determine which card is highlighted
  const highlightedPostId = selectedMovementEventId ? movementToPostId[selectedMovementEventId] : null

  // Handle selecting a sub-category — also set narrative filter so map filters too
  const handleSelectSubCategory = (type: string | null) => {
    setClusterSubCategory(type)
    setNarrativeFilter(type)
    if (!type && focusCluster) setFocusCluster(null)
  }

  if (loading) {
    return (
      <div className="h-full bg-[var(--bg-panel)] px-3 py-3">
        <h2 className="text-[10px] font-medium text-[var(--text-dim)] uppercase tracking-[0.15em] mb-3 px-1">
          Intelligence Feed
        </h2>
        <div className="space-y-1">
          <div className="bg-white/[0.02] h-16 animate-pulse" />
          <div className="bg-white/[0.02] h-16 animate-pulse" />
          <div className="bg-white/[0.02] h-16 animate-pulse" />
        </div>
      </div>
    )
  }

  // Helper to render a flat list of feed items
  const renderFeedItems = (items: FeedItem[]) => {
    if (items.length === 0) {
      return (
        <div className="text-[11px] text-[var(--text-dim)] text-center py-8 font-mono">
          No intelligence data available
        </div>
      )
    }
    return (
      <div className="space-y-[1px]">
        {items.map((item, index) => {
          if (item.type === 'article') {
            const isCoordinated = coordinatedArticleIds.has(item.data.id)
            const isSelected = selectedId === item.data.id
            return (
              <div key={`article-${item.data.id}-${index}`} ref={el => { cardRefs.current[item.data.id] = el }}>
                <ArticleCard
                  article={item.data}
                  isCoordinated={isCoordinated}
                  isSelected={isSelected}
                  onSelect={() => selectCard(item.data.id, 'article')}
                />
              </div>
            )
          } else {
            const isSelected = selectedId === item.data.id || highlightedPostId === item.data.id
            return (
              <div key={`post-${item.data.id}-${index}`} ref={el => { cardRefs.current[item.data.id] = el }}>
                <PostCard
                  post={item.data}
                  movementEvent={item.matchedEvent}
                  isSelected={isSelected}
                  onSelect={() => selectCard(item.data.id, 'post', item.matchedEvent?.id)}
                />
              </div>
            )
          }
        })}
      </div>
    )
  }

  return (
    <div className="h-full bg-[var(--bg-panel)] flex flex-col">
      {/* Header + filter tabs */}
      <div className="shrink-0 px-3 pt-3 pb-2">
        <h2 className="text-[10px] font-medium text-[var(--text-dim)] uppercase tracking-[0.15em] mb-2 px-1">
          Intelligence Feed
        </h2>

        <div className="flex items-center gap-[1px] px-1">
          {FILTER_OPTIONS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => handleSetFilter(key)}
              className={`flex items-center gap-1 px-2 py-1 text-[9px] font-mono uppercase tracking-wider transition-all duration-150 ${
                feedFilter === key
                  ? 'text-[var(--text-primary)] border border-[var(--border-active)] bg-white/[0.03]'
                  : 'text-[var(--text-dim)] hover:text-[var(--text-muted)] border border-transparent'
              }`}
            >
              <Icon size={9} />
              {label}
              <span className="tabular-nums text-[var(--text-dim)] ml-0.5">{counts[key]}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Sub-category chips — shown when Clusters tab active */}
      {feedFilter === 'clusters' && Object.keys(clustersByType).length > 0 && (
        <div className="shrink-0 px-3 pb-2">
          <div className="flex items-center gap-1 px-1 flex-wrap">
            {Object.entries(clustersByType).map(([type, typeClusters]) => {
              const totalEvents = typeClusters.reduce((sum, c) => sum + c.points.length, 0)
              return (
                <button
                  key={type}
                  onClick={() => handleSelectSubCategory(clusterSubCategory === type ? null : type)}
                  className={`flex items-center gap-1 px-1.5 py-0.5 text-[8px] font-mono uppercase tracking-wider transition-all duration-150 ${
                    clusterSubCategory === type
                      ? 'text-[var(--text-primary)] border border-[var(--border-active)] bg-white/[0.03]'
                      : 'text-[var(--text-dim)] hover:text-[var(--text-muted)] border border-transparent'
                  }`}
                >
                  <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: EVENT_TYPE_COLORS[type] || '#6b7280' }} />
                  {type.replace(/_/g, ' ')}
                  <span className="tabular-nums">{totalEvents}</span>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Feed content */}
      <div className="flex-1 overflow-y-auto px-3 pb-3 min-h-0">

        {/* === CLUSTERS TAB === */}
        {feedFilter === 'clusters' ? (
          !clusterSubCategory || !subCategoryClusters ? (
            <div className="text-[11px] text-[var(--text-dim)] text-center py-8 font-mono">
              {Object.keys(clustersByType).length === 0
                ? 'No clusters detected yet'
                : 'Select a category above'}
            </div>
          ) : subCategoryClusters.length === 0 ? (
            <div className="text-[11px] text-[var(--text-dim)] text-center py-8 font-mono">
              No clusters for this type
            </div>
          ) : (
            <div className="space-y-3">
              {subCategoryClusters.map(({ cluster, items }) => {
                const isFocused = focusCluster?.id === cluster.id
                const hasIndividualSelection = isFocused && !!selectedMovementEventId
                const showClusterBorder = isFocused && !hasIndividualSelection
                const clusterColor = EVENT_TYPE_COLORS[cluster.type] || '#6b7280'
                return (
                  <div
                    key={cluster.id}
                    className="transition-all duration-200 border"
                    style={showClusterBorder
                      ? { borderColor: clusterColor, boxShadow: `0 0 12px -2px ${clusterColor}30, inset 0 0 16px -6px ${clusterColor}15` }
                      : { borderColor: 'transparent' }
                    }
                  >
                    {/* Cluster header — click to focus on map */}
                    <button
                      onClick={() => { clearSelection(); setFocusCluster(isFocused ? null : cluster) }}
                      className={`flex items-center gap-2 w-full px-2.5 py-2 transition-all duration-200 ${
                        showClusterBorder
                          ? 'bg-white/[0.06]'
                          : 'bg-white/[0.02] hover:bg-white/[0.04]'
                      }`}
                    >
                      <div
                        className="w-2 h-2 rounded-full shrink-0 transition-all duration-200"
                        style={{
                          background: showClusterBorder ? clusterColor : hasIndividualSelection ? '#555555' : clusterColor,
                          boxShadow: showClusterBorder ? `0 0 6px ${clusterColor}80` : 'none',
                        }}
                      />
                      <span className={`text-[9px] font-mono tabular-nums transition-colors ${showClusterBorder ? 'text-[var(--text-primary)]' : 'text-[var(--text-muted)]'}`}>
                        {formatEventTime(cluster.startTime)} — {formatEventTime(cluster.endTime)}
                      </span>
                      <span className={`text-[9px] font-mono tabular-nums ml-auto transition-colors ${showClusterBorder ? 'text-[var(--text-muted)]' : 'text-[var(--text-dim)]'}`}>
                        {cluster.points.length} events
                      </span>
                      {showClusterBorder && (
                        <span className="text-[8px] font-mono uppercase tracking-wider text-[var(--text-primary)] ml-1">Active</span>
                      )}
                    </button>

                    {/* Cluster event cards — clicking focuses this cluster on map */}
                    <div className="space-y-[1px]">
                      {items.length > 0 ? items.map((item, index) => {
                        if (item.type === 'article') {
                          const isCoordinated = coordinatedArticleIds.has(item.data.id)
                          const isSelected = selectedId === item.data.id
                          return (
                            <div key={`article-${item.data.id}-${index}`} ref={el => { cardRefs.current[item.data.id] = el }}>
                              <ArticleCard
                                article={item.data}
                                isCoordinated={isCoordinated}
                                isSelected={isSelected}
                                onSelect={() => { setFocusCluster(cluster); selectCard(item.data.id, 'article') }}
                              />
                            </div>
                          )
                        } else {
                          const isSelected = selectedId === item.data.id || highlightedPostId === item.data.id
                          return (
                            <div key={`post-${item.data.id}-${index}`} ref={el => { cardRefs.current[item.data.id] = el }}>
                              <PostCard
                                post={item.data}
                                movementEvent={item.matchedEvent}
                                isSelected={isSelected}
                                onSelect={() => { setFocusCluster(cluster); selectCard(item.data.id, 'post', item.matchedEvent?.id) }}
                              />
                            </div>
                          )
                        }
                      }) : cluster.points.map(point => (
                        <ClusterEventCard
                          key={point.id}
                          point={point}
                          isSelected={selectedMovementEventId === point.id}
                          onSelect={() => { setFocusCluster(cluster); selectFromMap(point.id) }}
                        />
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          )
        ) : (
          /* === ALL / HIGH TABS — flat feed === */
          renderFeedItems(filteredItems)
        )}
      </div>
    </div>
  )
}
