import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { RealtimeChannel } from '@supabase/supabase-js'

export interface HeatmapPoint {
  lat: number
  lon: number
  type: string
}

export function useMovementHeatmap() {
  const [heatmapPoints, setHeatmapPoints] = useState<HeatmapPoint[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let channel: RealtimeChannel | null = null
    let mounted = true

    async function initialize() {
      try {
        // Fetch all movement_events with location data
        const { data, error } = await supabase
          .from('movement_events')
          .select('location_lat, location_lon, event_type')

        if (error) throw error

        if (mounted && data) {
          // Filter out rows where location_lat or location_lon is null
          const points = data
            .filter((event) => event.location_lat !== null && event.location_lon !== null)
            .map((event) => ({
              lat: event.location_lat!,
              lon: event.location_lon!,
              type: event.event_type,
            }))

          setHeatmapPoints(points)
          setLoading(false)
        }

        // Subscribe to realtime INSERT events on movement_events
        channel = supabase
          .channel('movement_events_heatmap')
          .on(
            'postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'movement_events',
            },
            (payload) => {
              if (!mounted) return

              const newEvent = payload.new as any

              // Only add if location data exists
              if (newEvent.location_lat !== null && newEvent.location_lon !== null) {
                setHeatmapPoints((prev) => [
                  ...prev,
                  {
                    lat: newEvent.location_lat,
                    lon: newEvent.location_lon,
                    type: newEvent.event_type,
                  },
                ])
              }
            }
          )
          .subscribe()
      } catch (err) {
        console.error('useMovementHeatmap error:', err)
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

  return { heatmapPoints, loading }
}
