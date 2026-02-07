import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { Brief } from '../types/database'

const POLL_INTERVAL = 2000

export function useBriefs(): { brief: Brief | null; loading: boolean } {
  const [brief, setBrief] = useState<Brief | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchBrief = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('briefs')
        .select('*')
        .order('generated_at', { ascending: false })
        .limit(1)

      if (error) throw error
      setBrief(data && data.length > 0 ? data[0] : null)
    } catch (err) {
      console.error('Error fetching latest brief:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchBrief()
    const interval = setInterval(fetchBrief, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchBrief])

  return { brief, loading }
}
