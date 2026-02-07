import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { RealtimeChannel } from '@supabase/supabase-js'

interface UseRealtimeSubscriptionOptions<T> {
  table: string
  filter?: string
  event?: 'INSERT' | 'UPDATE' | 'DELETE' | '*'
  orderBy?: { column: string; ascending?: boolean }
  limit?: number
}

export function useRealtimeSubscription<T>(
  options: UseRealtimeSubscriptionOptions<T>
) {
  const { table, filter, event = '*', orderBy, limit } = options
  const [data, setData] = useState<T[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let channel: RealtimeChannel | null = null
    let mounted = true

    async function initialize() {
      try {
        // Initial fetch
        let query = supabase.from(table).select('*')

        if (orderBy) {
          query = query.order(orderBy.column, { ascending: orderBy.ascending ?? false })
        }

        if (limit) {
          query = query.limit(limit)
        }

        const { data: initialData, error: fetchError } = await query

        if (fetchError) throw fetchError

        if (mounted) {
          setData((initialData as T[]) || [])
          setLoading(false)
        }

        // Set up realtime subscription
        channel = supabase
          .channel(`${table}_changes`)
          .on(
            'postgres_changes',
            {
              event: event,
              schema: 'public',
              table: table,
              filter: filter,
            },
            (payload) => {
              if (!mounted) return

              if (payload.eventType === 'INSERT') {
                setData((prev) => [payload.new as T, ...prev])
              } else if (payload.eventType === 'UPDATE') {
                setData((prev) =>
                  prev.map((item: any) =>
                    item.id === (payload.new as any).id ? (payload.new as T) : item
                  )
                )
              } else if (payload.eventType === 'DELETE') {
                setData((prev) =>
                  prev.filter((item: any) => item.id !== (payload.old as any).id)
                )
              }
            }
          )
          .subscribe()
      } catch (err) {
        if (mounted) {
          setError(err as Error)
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
  }, [table, filter, event, orderBy?.column, orderBy?.ascending, limit])

  return { data, loading, error }
}
