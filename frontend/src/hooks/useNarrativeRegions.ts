import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'

export interface NarrativeRegion {
  name: string
  polygon: number[][] // [lon, lat] pairs for bounding box
  eventCount: number
}

const GEOGRAPHIC_REGIONS: Record<string, { name: string; polygon: number[][] }> = {
  'taiwan strait': {
    name: 'Taiwan Strait',
    polygon: [
      [117.5, 22.5],
      [121.5, 22.5],
      [121.5, 26.0],
      [117.5, 26.0],
      [117.5, 22.5],
    ],
  },
  strait: {
    name: 'Taiwan Strait',
    polygon: [
      [117.5, 22.5],
      [121.5, 22.5],
      [121.5, 26.0],
      [117.5, 26.0],
      [117.5, 22.5],
    ],
  },
  taiwan: {
    name: 'Taiwan Strait',
    polygon: [
      [117.5, 22.5],
      [121.5, 22.5],
      [121.5, 26.0],
      [117.5, 26.0],
      [117.5, 22.5],
    ],
  },
  'south china sea': {
    name: 'South China Sea',
    polygon: [
      [110.0, 5.0],
      [121.0, 5.0],
      [121.0, 22.0],
      [110.0, 22.0],
      [110.0, 5.0],
    ],
  },
  'south china': {
    name: 'South China Sea',
    polygon: [
      [110.0, 5.0],
      [121.0, 5.0],
      [121.0, 22.0],
      [110.0, 22.0],
      [110.0, 5.0],
    ],
  },
  'east china sea': {
    name: 'East China Sea',
    polygon: [
      [120.0, 25.0],
      [130.0, 25.0],
      [130.0, 33.0],
      [120.0, 33.0],
      [120.0, 25.0],
    ],
  },
  'east china': {
    name: 'East China Sea',
    polygon: [
      [120.0, 25.0],
      [130.0, 25.0],
      [130.0, 33.0],
      [120.0, 33.0],
      [120.0, 25.0],
    ],
  },
}

function extractRegionsFromEvents(events: any[]): NarrativeRegion[] {
  const regionCounts = new Map<string, number>()

  for (const event of events) {
    const text = `${event.event_type || ''} ${event.summary || ''}`.toLowerCase()
    for (const [keyword, region] of Object.entries(GEOGRAPHIC_REGIONS)) {
      if (text.includes(keyword)) {
        const count = regionCounts.get(region.name) || 0
        regionCounts.set(region.name, count + 1)
      }
    }
  }

  const regions: NarrativeRegion[] = []
  for (const [name, eventCount] of regionCounts.entries()) {
    const regionDef = Object.values(GEOGRAPHIC_REGIONS).find((r) => r.name === name)
    if (regionDef) {
      regions.push({ name, polygon: regionDef.polygon, eventCount })
    }
  }
  return regions
}

const POLL_INTERVAL = 2000

export function useNarrativeRegions() {
  const [activeRegions, setActiveRegions] = useState<NarrativeRegion[]>([])
  const [loading, setLoading] = useState(true)

  const fetchRegions = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('narrative_events')
        .select('event_type, summary, detected_at')

      if (error) throw error

      if (data) {
        setActiveRegions(extractRegionsFromEvents(data))
      }
    } catch (err) {
      console.error('useNarrativeRegions error:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchRegions()
    const interval = setInterval(fetchRegions, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchRegions])

  return { activeRegions, loading }
}
