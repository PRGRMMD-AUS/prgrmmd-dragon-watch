import { useState, useEffect, useCallback, useRef } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface DemoStatus {
  state: 'idle' | 'playing' | 'paused'
  speed: number
  speed_label: string
  progress: number
  records_inserted: number
  total_records: number
  simulated_time: string
  simulated_hours: number
}

interface UseDemoControlReturn {
  status: DemoStatus | null
  start: (clearTables: boolean) => Promise<void>
  pause: () => Promise<void>
  reset: () => Promise<void>
  setSpeed: (speed: number) => Promise<void>
  loading: boolean
  error: string | null
}

export function useDemoControl(): UseDemoControlReturn {
  const [status, setStatus] = useState<DemoStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Fetch status from API
  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/demo/status`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setStatus(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch status')
    }
  }, [])

  // Start demo (clearTables: true on first start, false on resume)
  const start = useCallback(async (clearTables: boolean) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/demo/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ clear_tables: clearTables })
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setStatus(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start demo')
    } finally {
      setLoading(false)
    }
  }, [])

  // Pause demo
  const pause = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/demo/pause`, {
        method: 'POST'
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setStatus(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to pause demo')
    } finally {
      setLoading(false)
    }
  }, [])

  // Reset demo
  const reset = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/demo/reset`, {
        method: 'POST'
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setStatus(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset demo')
    } finally {
      setLoading(false)
    }
  }, [])

  // Set playback speed
  const setSpeed = useCallback(async (speed: number) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/demo/speed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ speed })
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setStatus(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to set speed')
    } finally {
      setLoading(false)
    }
  }, [])

  // Poll status when playing (every 500ms)
  useEffect(() => {
    if (status?.state === 'playing') {
      pollingIntervalRef.current = setInterval(fetchStatus, 500)
    } else {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [status?.state, fetchStatus])

  // Fetch initial status on mount
  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  return {
    status,
    start,
    pause,
    reset,
    setSpeed,
    loading,
    error
  }
}
