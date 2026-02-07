import { useEffect, useState, useCallback, useMemo } from 'react'
import { supabase } from '../lib/supabase'

export interface HeatmapPoint {
  id: string
  lat: number
  lon: number
  type: string
  detected_at: string
  vessel_mmsi: string
  description: string
}

export interface Cluster {
  id: string
  type: string
  points: HeatmapPoint[]
  startTime: string
  endTime: string
}

const POLL_INTERVAL = 2000
const CLUSTER_WINDOW_MS = 12 * 60 * 60 * 1000 // 12 hours

export function useMovementHeatmap() {
  const [heatmapPoints, setHeatmapPoints] = useState<HeatmapPoint[]>([])
  const [loading, setLoading] = useState(true)

  const fetchHeatmap = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('movement_events')
        .select('id, location_lat, location_lon, event_type, detected_at, vessel_mmsi, description')
        .order('detected_at', { ascending: true })

      if (error) throw error

      if (data) {
        const points = data
          .filter((event: any) => event.location_lat !== null && event.location_lon !== null)
          .map((event: any): HeatmapPoint => ({
            id: event.id as string,
            lat: event.location_lat as number,
            lon: event.location_lon as number,
            type: event.event_type as string,
            detected_at: event.detected_at as string,
            vessel_mmsi: event.vessel_mmsi as string,
            description: (event.description || '') as string,
          }))
        setHeatmapPoints(points)
      }
    } catch (err) {
      console.error('useMovementHeatmap error:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchHeatmap()
    const interval = setInterval(fetchHeatmap, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchHeatmap])

  // Detect clusters: group by event_type, then by temporal proximity
  const clusters = useMemo<Cluster[]>(() => {
    const grouped: Record<string, HeatmapPoint[]> = {}
    for (const pt of heatmapPoints) {
      if (!grouped[pt.type]) grouped[pt.type] = []
      grouped[pt.type].push(pt)
    }

    const result: Cluster[] = []
    for (const [type, points] of Object.entries(grouped)) {
      const sorted = [...points].sort(
        (a, b) => new Date(a.detected_at).getTime() - new Date(b.detected_at).getTime()
      )

      let currentCluster: HeatmapPoint[] = [sorted[0]]
      for (let i = 1; i < sorted.length; i++) {
        const prevTime = new Date(sorted[i - 1].detected_at).getTime()
        const currTime = new Date(sorted[i].detected_at).getTime()
        if (currTime - prevTime <= CLUSTER_WINDOW_MS) {
          currentCluster.push(sorted[i])
        } else {
          if (currentCluster.length >= 2) {
            result.push({
              id: `cluster-${type}-${currentCluster[0].id}`,
              type,
              points: currentCluster,
              startTime: currentCluster[0].detected_at,
              endTime: currentCluster[currentCluster.length - 1].detected_at,
            })
          }
          currentCluster = [sorted[i]]
        }
      }
      if (currentCluster.length >= 2) {
        result.push({
          id: `cluster-${type}-${currentCluster[0].id}`,
          type,
          points: currentCluster,
          startTime: currentCluster[0].detected_at,
          endTime: currentCluster[currentCluster.length - 1].detected_at,
        })
      }
    }

    return result.sort((a, b) => b.points.length - a.points.length)
  }, [heatmapPoints])

  // Map from point ID → cluster ID for quick lookup
  const pointClusterMap = useMemo(() => {
    const map: Record<string, string> = {}
    for (const cluster of clusters) {
      for (const pt of cluster.points) {
        map[pt.id] = cluster.id
      }
    }
    return map
  }, [clusters])

  return { heatmapPoints, clusters, pointClusterMap, loading }
}
