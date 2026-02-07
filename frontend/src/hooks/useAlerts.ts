import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import type { Alert } from '../types/database'
import { RealtimeChannel } from '@supabase/supabase-js'

export function useAlerts() {
  const [alert, setAlert] = useState<Alert | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let channel: RealtimeChannel | null = null
    let mounted = true

    async function initialize() {
      try {
        // Fetch most recent unresolved alert
        const { data, error } = await supabase
          .from('alerts')
          .select('*')
          .is('resolved_at', null)
          .order('created_at', { ascending: false })
          .limit(1)

        if (error) throw error

        if (mounted) {
          setAlert(data && data.length > 0 ? data[0] : null)
          setLoading(false)
        }

        // Subscribe to realtime INSERT and UPDATE events on alerts table
        channel = supabase
          .channel('alerts_changes')
          .on(
            'postgres_changes',
            {
              event: '*',
              schema: 'public',
              table: 'alerts',
            },
            (payload) => {
              if (!mounted) return

              const newAlert = payload.new as Alert

              // Only consider unresolved alerts
              if (newAlert && newAlert.resolved_at === null) {
                if (payload.eventType === 'INSERT' || payload.eventType === 'UPDATE') {
                  // Replace current alert if new one is more recent
                  setAlert((prev) => {
                    if (!prev) return newAlert
                    return new Date(newAlert.created_at) > new Date(prev.created_at)
                      ? newAlert
                      : prev
                  })
                }
              } else if (payload.eventType === 'UPDATE' && newAlert && newAlert.resolved_at !== null) {
                // Alert was resolved - clear if it's the current one
                setAlert((prev) => {
                  if (prev && prev.id === newAlert.id) return null
                  return prev
                })
              }
            }
          )
          .subscribe()
      } catch (err) {
        console.error('useAlerts error:', err)
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

  return { alert, loading }
}
