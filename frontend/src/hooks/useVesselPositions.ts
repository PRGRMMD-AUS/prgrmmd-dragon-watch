import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { VesselPosition } from '../types/database'

const POLL_INTERVAL = 2000

export function useVesselPositions() {
  const [vessels, setVessels] = useState<Map<string, VesselPosition>>(new Map())
  const [importantVessels, setImportantVessels] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)

  const fetchVessels = useCallback(async () => {
    try {
      const [positionsResult, movementResult] = await Promise.all([
        supabase
          .from('vessel_positions')
          .select('*')
          .order('timestamp', { ascending: false }),
        supabase
          .from('movement_events')
          .select('vessel_mmsi'),
      ])

      if (positionsResult.error) throw positionsResult.error

      if (positionsResult.data) {
        const vesselMap = new Map<string, VesselPosition>()
        for (const position of positionsResult.data) {
          if (!vesselMap.has(position.mmsi)) {
            vesselMap.set(position.mmsi, position)
          }
        }
        setVessels(vesselMap)
      }

      if (movementResult.data) {
        const mmsiSet = new Set<string>()
        for (const event of movementResult.data) {
          if (event.vessel_mmsi) mmsiSet.add(event.vessel_mmsi)
        }
        setImportantVessels(mmsiSet)
      }
    } catch (err) {
      console.error('useVesselPositions error:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchVessels()
    const interval = setInterval(fetchVessels, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchVessels])

  return { vessels, importantVessels, loading }
}
