import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { NarrativeEvent } from '../types/database'

interface DetectionHistoryPoint {
  detected_at: string
  score: number
  level: string
}

const POLL_INTERVAL = 2000

export function useNarrativeEvents() {
  const [events, setEvents] = useState<NarrativeEvent[]>([])
  const [coordinatedArticleIds, setCoordinatedArticleIds] = useState<Set<string>>(new Set())
  const [detectionHistory, setDetectionHistory] = useState<DetectionHistoryPoint[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('narrative_events')
        .select('*')
        .order('detected_at', { ascending: true })

      if (error) throw error

      const narrativeEvents = data || []
      setEvents(narrativeEvents)

      // Build Set of coordinated article IDs from source_ids
      const articleIds = new Set<string>()
      narrativeEvents.forEach((event) => {
        if (event.source_ids && Array.isArray(event.source_ids)) {
          event.source_ids.forEach((id: string) => articleIds.add(id))
        }
      })
      setCoordinatedArticleIds(articleIds)

      // Fetch alert detection_history from correlation_metadata
      const { data: alertData } = await supabase
        .from('alerts')
        .select('correlation_metadata')
        .order('created_at', { ascending: false })
        .limit(1)

      if (alertData && alertData.length > 0) {
        const metadata = alertData[0].correlation_metadata
        if (metadata && metadata.detection_history && Array.isArray(metadata.detection_history)) {
          setDetectionHistory(metadata.detection_history)
        }
      }
    } catch (err) {
      console.error('Error loading narrative events:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchData])

  return { events, coordinatedArticleIds, detectionHistory, loading }
}
