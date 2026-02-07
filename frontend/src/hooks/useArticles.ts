import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { Article } from '../types/database'

const POLL_INTERVAL = 2000

export function useArticles() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)

  const fetchArticles = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('articles')
        .select('*')
        .order('published_at', { ascending: false })
        .limit(50)

      if (error) throw error
      setArticles(data || [])
    } catch (err) {
      console.error('Error loading articles:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchArticles()
    const interval = setInterval(fetchArticles, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchArticles])

  return { articles, loading }
}
