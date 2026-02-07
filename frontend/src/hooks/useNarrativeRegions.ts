import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { RealtimeChannel } from '@supabase/supabase-js'

export interface NarrativeRegion {
  name: string
  polygon: number[][] // [lon, lat] pairs for bounding box
  eventCount: number
}

// Predefined geographic term to bounding region mappings
const GEOGRAPHIC_REGIONS: Record<string, { name: string; polygon: number[][] }> = {
  'taiwan strait': {
    name: 'Taiwan Strait',
    polygon: [
      [117.5, 22.5],
      [121.5, 22.5],
      [121.5, 26.0],
      [117.5, 26.0],
      [117.5, 22.5], // Close the polygon
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

export function useNarrativeRegions() {
  const [activeRegions, setActiveRegions] = useState<NarrativeRegion[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let channel: RealtimeChannel | null = null
    let mounted = true

    function extractRegionsFromEvents(events: any[]): NarrativeRegion[] {
      const regionCounts = new Map<string, number>()

      // Scan each event for geographic keywords
      for (const event of events) {
        const text = `${event.event_type || ''} ${event.summary || ''}`.toLowerCase()

        // Check for each known geographic term
        for (const [keyword, region] of Object.entries(GEOGRAPHIC_REGIONS)) {
          if (text.includes(keyword)) {
            const count = regionCounts.get(region.name) || 0
            regionCounts.set(region.name, count + 1)
          }
        }
      }

      // Convert to array of NarrativeRegion objects
      const regions: NarrativeRegion[] = []
      for (const [name, eventCount] of regionCounts.entries()) {
        // Find the region definition (use first matching keyword)
        const regionDef = Object.values(GEOGRAPHIC_REGIONS).find((r) => r.name === name)
        if (regionDef) {
          regions.push({
            name,
            polygon: regionDef.polygon,
            eventCount,
          })
        }
      }

      return regions
    }

    async function initialize() {
      try {
        // Fetch all narrative_events
        const { data, error } = await supabase
          .from('narrative_events')
          .select('event_type, summary, detected_at')

        if (error) throw error

        if (mounted && data) {
          const regions = extractRegionsFromEvents(data)
          setActiveRegions(regions)
          setLoading(false)
        }

        // Subscribe to realtime INSERT events on narrative_events
        channel = supabase
          .channel('narrative_events_regions')
          .on(
            'postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'narrative_events',
            },
            (payload) => {
              if (!mounted) return

              // Re-fetch all events to recalculate regions
              // (This is simpler than incremental updates for the demo)
              supabase
                .from('narrative_events')
                .select('event_type, summary, detected_at')
                .then(({ data, error }) => {
                  if (!error && data && mounted) {
                    const regions = extractRegionsFromEvents(data)
                    setActiveRegions(regions)
                  }
                })
            }
          )
          .subscribe()
      } catch (err) {
        console.error('useNarrativeRegions error:', err)
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

  return { activeRegions, loading }
}
