import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import type { VesselPosition } from '../types/database'
import { RealtimeChannel } from '@supabase/supabase-js'

export function useVesselPositions() {
  const [vessels, setVessels] = useState<Map<string, VesselPosition>>(new Map())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let channel: RealtimeChannel | null = null
    let mounted = true

    async function initialize() {
      try {
        // Fetch all vessel positions, ordered by timestamp descending
        const { data, error } = await supabase
          .from('vessel_positions')
          .select('*')
          .order('timestamp', { ascending: false })

        if (error) throw error

        if (mounted && data) {
          // Group by MMSI - keep only the latest position per vessel
          const vesselMap = new Map<string, VesselPosition>()
          for (const position of data) {
            if (!vesselMap.has(position.mmsi)) {
              vesselMap.set(position.mmsi, position)
            }
          }
          setVessels(vesselMap)
          setLoading(false)
        }

        // Subscribe to realtime INSERT events on vessel_positions
        channel = supabase
          .channel('vessel_positions_changes')
          .on(
            'postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'vessel_positions',
            },
            (payload) => {
              if (!mounted) return

              const newPosition = payload.new as VesselPosition

              // Update the vessel's position (latest position per MMSI)
              setVessels((prev) => {
                const updated = new Map(prev)
                const existing = updated.get(newPosition.mmsi)

                // Only update if this position is newer than the current one
                if (!existing || new Date(newPosition.timestamp) > new Date(existing.timestamp)) {
                  updated.set(newPosition.mmsi, newPosition)
                }

                return updated
              })
            }
          )
          .subscribe()
      } catch (err) {
        console.error('useVesselPositions error:', err)
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

  return { vessels, loading }
}
