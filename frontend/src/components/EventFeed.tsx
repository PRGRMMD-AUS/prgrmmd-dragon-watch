import { useMemo } from 'react'
import { useArticles } from '../hooks/useArticles'
import { useSocialPosts } from '../hooks/useSocialPosts'
import { useNarrativeEvents } from '../hooks/useNarrativeEvents'
import { useMovementEvents } from '../hooks/useMovementEvents'
import { ArticleCard } from './ArticleCard'
import { PostCard } from './PostCard'
import type { Article, SocialPost, MovementEvent } from '../types/database'

type FeedItem =
  | { type: 'article'; data: Article; sortTime: string }
  | { type: 'post'; data: SocialPost; sortTime: string }

// Find closest movement event within 5 minutes
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

export function EventFeed() {
  const { articles, loading: articlesLoading } = useArticles()
  const { posts, loading: postsLoading } = useSocialPosts()
  const { coordinatedArticleIds, loading: narrativeLoading } = useNarrativeEvents()
  const { movementEvents, loading: movementLoading } = useMovementEvents()

  // Combine and sort articles and posts by timestamp
  const feedItems = useMemo<FeedItem[]>(() => {
    const items: FeedItem[] = []

    // Add articles
    articles.forEach((article) => {
      items.push({
        type: 'article',
        data: article,
        sortTime: article.published_at,
      })
    })

    // Add posts
    posts.forEach((post) => {
      items.push({
        type: 'post',
        data: post,
        sortTime: post.timestamp,
      })
    })

    // Sort by timestamp, most recent first
    items.sort((a, b) => {
      return new Date(b.sortTime).getTime() - new Date(a.sortTime).getTime()
    })

    return items
  }, [articles, posts])

  const loading = articlesLoading || postsLoading || narrativeLoading || movementLoading

  if (loading) {
    return (
      <div className="h-full bg-gray-50 px-3 py-2">
        <h2 className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-3">
          Intelligence Feed
        </h2>
        {/* Skeleton loader */}
        <div className="space-y-2">
          <div className="bg-gray-200 rounded-lg h-20 animate-pulse" />
          <div className="bg-gray-200 rounded-lg h-20 animate-pulse" />
          <div className="bg-gray-200 rounded-lg h-20 animate-pulse" />
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-gray-50 overflow-y-auto px-3 py-2">
      <h2 className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-3">
        Intelligence Feed
      </h2>

      {feedItems.length === 0 ? (
        <div className="text-sm text-gray-500 text-center py-8">
          No intelligence data available
        </div>
      ) : (
        <div>
          {feedItems.map((item, index) => {
            if (item.type === 'article') {
              const isCoordinated = coordinatedArticleIds.has(item.data.id)
              return (
                <ArticleCard
                  key={`article-${item.data.id}-${index}`}
                  article={item.data}
                  isCoordinated={isCoordinated}
                />
              )
            } else {
              // Find matching movement event for this post
              const matchedEvent = findMatchingMovementEvent(item.data.timestamp, movementEvents)
              return (
                <PostCard
                  key={`post-${item.data.id}-${index}`}
                  post={item.data}
                  movementEvent={matchedEvent}
                />
              )
            }
          })}
        </div>
      )}
    </div>
  )
}
