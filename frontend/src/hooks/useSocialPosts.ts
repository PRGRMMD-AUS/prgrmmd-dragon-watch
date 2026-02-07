import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { SocialPost } from '../types/database'
import { RealtimeChannel } from '@supabase/supabase-js'

export function useSocialPosts() {
  const [posts, setPosts] = useState<SocialPost[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let channel: RealtimeChannel | null = null
    let mounted = true

    async function initialize() {
      try {
        // Initial fetch - 50 most recent posts
        const { data, error } = await supabase
          .from('social_posts')
          .select('*')
          .order('timestamp', { ascending: false })
          .limit(50)

        if (error) throw error

        if (mounted) {
          setPosts(data || [])
          setLoading(false)
        }

        // Set up realtime subscription for new posts
        channel = supabase
          .channel('social_posts_changes')
          .on(
            'postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'social_posts',
            },
            (payload) => {
              if (!mounted) return
              // Prepend new post to the top
              setPosts((prev) => [payload.new as SocialPost, ...prev])
            }
          )
          .subscribe()
      } catch (err) {
        console.error('Error loading social posts:', err)
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

  return { posts, loading }
}
