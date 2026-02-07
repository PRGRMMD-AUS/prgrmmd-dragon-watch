import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { MovementEvent } from '../types/database'

const POLL_INTERVAL = 2000

export function useMovementEvents() {
  const [movementEvents, setMovementEvents] = useState<MovementEvent[]>([])
  const [loading, setLoading] = useState(true)

  const fetchMovementEvents = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('movement_events')
        .select('*')
        .order('detected_at', { ascending: false })

      if (error) throw error
      setMovementEvents(data || [])
    } catch (err) {
      console.error('Error loading movement events:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMovementEvents()
    const interval = setInterval(fetchMovementEvents, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchMovementEvents])

  return { movementEvents, loading }
}
