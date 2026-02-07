import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { NarrativeEvent } from '../types/database'
import { RealtimeChannel } from '@supabase/supabase-js'

interface DetectionHistoryPoint {
  detected_at: string
  score: number
  level: string
}

export function useNarrativeEvents() {
  const [events, setEvents] = useState<NarrativeEvent[]>([])
  const [coordinatedArticleIds, setCoordinatedArticleIds] = useState<Set<string>>(new Set())
  const [detectionHistory, setDetectionHistory] = useState<DetectionHistoryPoint[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let channel: RealtimeChannel | null = null
    let mounted = true

    async function initialize() {
      try {
        // Fetch all narrative events
        const { data, error } = await supabase
          .from('narrative_events')
          .select('*')
          .order('detected_at', { ascending: true })

        if (error) throw error

        if (mounted) {
          const narrativeEvents = data || []
          setEvents(narrativeEvents)

          // Build Set of coordinated article IDs from source_ids
          const articleIds = new Set<string>()
          narrativeEvents.forEach((event) => {
            if (event.source_ids && Array.isArray(event.source_ids)) {
              event.source_ids.forEach((id) => articleIds.add(id))
            }
          })
          setCoordinatedArticleIds(articleIds)
        }

        // Fetch alert to get detection_history from correlation_metadata
        const { data: alertData, error: alertError } = await supabase
          .from('alerts')
          .select('correlation_metadata')
          .order('created_at', { ascending: false })
          .limit(1)
          .single()

        if (!alertError && alertData && mounted) {
          const metadata = alertData.correlation_metadata
          if (metadata && metadata.detection_history && Array.isArray(metadata.detection_history)) {
            setDetectionHistory(metadata.detection_history)
          }
        }

        if (mounted) {
          setLoading(false)
        }

        // Set up realtime subscription for new narrative events
        channel = supabase
          .channel('narrative_events_changes')
          .on(
            'postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'narrative_events',
            },
            (payload) => {
              if (!mounted) return
              const newEvent = payload.new as NarrativeEvent
              setEvents((prev) => [...prev, newEvent])

              // Add new coordinated article IDs
              if (newEvent.source_ids && Array.isArray(newEvent.source_ids)) {
                setCoordinatedArticleIds((prev) => {
                  const updated = new Set(prev)
                  newEvent.source_ids.forEach((id) => updated.add(id))
                  return updated
                })
              }
            }
          )
          .subscribe()
      } catch (err) {
        console.error('Error loading narrative events:', err)
        if (mounted) {
          setLoading(false)
        }
      }
    }

    initialize()

    return () => {
      mounted = false
      if (channel) {
        supabase.removeChannel(channel)
      }
    }
  }, [])

  return { events, coordinatedArticleIds, detectionHistory, loading }
}
