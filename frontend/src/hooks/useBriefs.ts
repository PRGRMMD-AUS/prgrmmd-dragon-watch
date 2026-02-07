import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { Brief } from '../types/database'

interface UseBriefsReturn {
  brief: Brief | null
  loading: boolean
}

export function useBriefs(): UseBriefsReturn {
  const [brief, setBrief] = useState<Brief | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch the most recent brief on mount
    const fetchLatestBrief = async () => {
      try {
        const { data, error } = await supabase
          .from('briefs')
          .select('*')
          .order('generated_at', { ascending: false })
          .limit(1)
          .single()

        if (error) {
          if (error.code === 'PGRST116') {
            // No rows returned - empty state is expected
            setBrief(null)
          } else {
            console.error('Error fetching latest brief:', error)
          }
        } else {
          setBrief(data)
        }
      } catch (err) {
        console.error('Exception fetching latest brief:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchLatestBrief()

    // Subscribe to new briefs
    const channel = supabase
      .channel('briefs-changes')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'briefs',
        },
        (payload) => {
          console.log('New brief received:', payload)
          setBrief(payload.new as Brief)
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  return { brief, loading }
}
