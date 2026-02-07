import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import type { MovementEvent } from '../types/database'
import type { RealtimeChannel } from '@supabase/supabase-js'

export function useMovementEvents() {
  const [movementEvents, setMovementEvents] = useState<MovementEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let channel: RealtimeChannel | null = null
    let mounted = true

    async function initialize() {
      try {
        // Fetch all movement events
        const { data, error } = await supabase
          .from('movement_events')
          .select('*')
          .order('detected_at', { ascending: false })

        if (error) throw error

        if (mounted) {
          setMovementEvents(data || [])
          setLoading(false)
        }

        // Set up realtime subscription for new movement events
        channel = supabase
          .channel('movement_events_changes')
          .on(
            'postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'movement_events',
            },
            (payload) => {
              if (!mounted) return
              setMovementEvents((prev) => [payload.new as MovementEvent, ...prev])
            }
          )
          .subscribe()
      } catch (err) {
        console.error('Error loading movement events:', err)
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

  return { movementEvents, loading }
}
