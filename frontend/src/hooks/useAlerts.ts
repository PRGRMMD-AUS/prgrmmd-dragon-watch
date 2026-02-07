import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { Alert } from '../types/database'

const POLL_INTERVAL = 2000

export function useAlerts() {
  const [alert, setAlert] = useState<Alert | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchAlert = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('alerts')
        .select('*')
        .is('resolved_at', null)
        .order('created_at', { ascending: false })
        .limit(1)

      if (error) throw error
      setAlert(data && data.length > 0 ? data[0] : null)
    } catch (err) {
      console.error('useAlerts error:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAlert()
    const interval = setInterval(fetchAlert, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchAlert])

  return { alert, loading }
}
