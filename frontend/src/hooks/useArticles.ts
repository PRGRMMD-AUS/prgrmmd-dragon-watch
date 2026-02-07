import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { Article } from '../types/database'
import { RealtimeChannel } from '@supabase/supabase-js'

export function useArticles() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let channel: RealtimeChannel | null = null
    let mounted = true

    async function initialize() {
      try {
        // Initial fetch - 50 most recent articles
        const { data, error } = await supabase
          .from('articles')
          .select('*')
          .order('published_at', { ascending: false })
          .limit(50)

        if (error) throw error

        if (mounted) {
          setArticles(data || [])
          setLoading(false)
        }

        // Set up realtime subscription for new articles
        channel = supabase
          .channel('articles_changes')
          .on(
            'postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'articles',
            },
            (payload) => {
              if (!mounted) return
              // Prepend new article to the top
              setArticles((prev) => [payload.new as Article, ...prev])
            }
          )
          .subscribe()
      } catch (err) {
        console.error('Error loading articles:', err)
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

  return { articles, loading }
}
