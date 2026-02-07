import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { SocialPost } from '../types/database'

const POLL_INTERVAL = 2000

export function useSocialPosts() {
  const [posts, setPosts] = useState<SocialPost[]>([])
  const [loading, setLoading] = useState(true)

  const fetchPosts = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('social_posts')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(50)

      if (error) throw error
      setPosts(data || [])
    } catch (err) {
      console.error('Error loading social posts:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchPosts()
    const interval = setInterval(fetchPosts, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchPosts])

  return { posts, loading }
}
