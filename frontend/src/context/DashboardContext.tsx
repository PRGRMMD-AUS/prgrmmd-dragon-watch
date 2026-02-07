import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import type { HeatmapPoint, Cluster } from '../hooks/useMovementHeatmap'

export type FeedFilter = 'all' | 'clusters' | 'high-threat'

export interface EscalationTarget {
  eventId: string
  eventType: string
  description: string
}

interface DashboardContextType {
  // Selection
  selectedId: string | null
  selectedType: 'article' | 'post' | null
  selectedMovementEventId: string | null
  selectCard: (id: string, type: 'article' | 'post', movementEventId?: string | null) => void
  selectFromMap: (movementEventId: string) => void
  clearSelection: () => void

  // Map popup
  popupPoint: HeatmapPoint | null
  setPopupPoint: (point: HeatmapPoint | null) => void

  // Narrative filter
  narrativeFilter: string | null
  setNarrativeFilter: (eventType: string | null) => void

  // Timeline
  timelinePosition: number
  setTimelinePosition: (pos: number) => void

  // Escalation
  escalatedIds: Set<string>
  escalateEvent: (id: string) => void
  escalationTarget: EscalationTarget | null
  startEscalation: (target: EscalationTarget) => void
  submitEscalation: (department: string, person: string) => void
  cancelEscalation: () => void

  // Cluster focus
  focusCluster: Cluster | null
  setFocusCluster: (cluster: Cluster | null) => void

  // Feed filter
  feedFilter: FeedFilter
  setFeedFilter: (filter: FeedFilter) => void

  // Toast
  toast: string | null
}

const DashboardContext = createContext<DashboardContextType | null>(null)

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedType, setSelectedType] = useState<'article' | 'post' | null>(null)
  const [selectedMovementEventId, setSelectedMovementEventId] = useState<string | null>(null)
  const [popupPoint, setPopupPointRaw] = useState<HeatmapPoint | null>(null)
  const [narrativeFilter, setNarrativeFilterRaw] = useState<string | null>(null)
  const [timelinePosition, setTimelinePosition] = useState(100)
  const [escalatedIds, setEscalatedIds] = useState<Set<string>>(new Set())
  const [escalationTarget, setEscalationTarget] = useState<EscalationTarget | null>(null)
  const [focusCluster, setFocusClusterRaw] = useState<Cluster | null>(null)
  const [feedFilter, setFeedFilter] = useState<FeedFilter>('all')
  const [toast, setToast] = useState<string | null>(null)

  const selectCard = useCallback((id: string, type: 'article' | 'post', movementEventId?: string | null) => {
    setSelectedId(prev => {
      if (prev === id) {
        setSelectedType(null)
        setSelectedMovementEventId(null)
        setPopupPointRaw(null)
        return null
      }
      setSelectedType(type)
      setSelectedMovementEventId(movementEventId || null)
      return id
    })
  }, [])

  const selectFromMap = useCallback((movementEventId: string) => {
    setSelectedMovementEventId(prev => {
      if (prev === movementEventId) {
        setSelectedId(null)
        setSelectedType(null)
        setPopupPointRaw(null)
        return null
      }
      setSelectedId(null)
      setSelectedType(null)
      return movementEventId
    })
  }, [])

  const clearSelection = useCallback(() => {
    setSelectedId(null)
    setSelectedType(null)
    setSelectedMovementEventId(null)
    setPopupPointRaw(null)
    setNarrativeFilterRaw(null)
    setFocusClusterRaw(null)
  }, [])

  const setPopupPoint = useCallback((point: HeatmapPoint | null) => {
    setPopupPointRaw(point)
    if (point) {
      setSelectedMovementEventId(point.id)
    }
  }, [])

  const setNarrativeFilter = useCallback((eventType: string | null) => {
    setNarrativeFilterRaw(prev => prev === eventType ? null : eventType)
  }, [])

  const escalateEvent = useCallback((id: string) => {
    setEscalatedIds(prev => {
      const next = new Set(prev)
      next.add(id)
      return next
    })
    setToast('ESCALATED TO COMMAND')
    setTimeout(() => setToast(null), 3000)
  }, [])

  const startEscalation = useCallback((target: EscalationTarget) => {
    setEscalationTarget(target)
  }, [])

  const submitEscalation = useCallback((department: string, person: string) => {
    if (escalationTarget) {
      setEscalatedIds(prev => {
        const next = new Set(prev)
        next.add(escalationTarget.eventId)
        return next
      })
      setToast(`ESCALATED TO ${department.toUpperCase()} — ${person.toUpperCase()}`)
      setTimeout(() => setToast(null), 4000)
      setEscalationTarget(null)
    }
  }, [escalationTarget])

  const cancelEscalation = useCallback(() => {
    setEscalationTarget(null)
  }, [])

  const setFocusCluster = useCallback((cluster: Cluster | null) => {
    setFocusClusterRaw(cluster)
    if (cluster) {
      setPopupPointRaw(null)
    }
  }, [])

  return (
    <DashboardContext.Provider value={{
      selectedId,
      selectedType,
      selectedMovementEventId,
      selectCard,
      selectFromMap,
      clearSelection,
      popupPoint,
      setPopupPoint,
      narrativeFilter,
      setNarrativeFilter,
      timelinePosition,
      setTimelinePosition,
      escalatedIds,
      escalateEvent,
      escalationTarget,
      startEscalation,
      submitEscalation,
      cancelEscalation,
      focusCluster,
      setFocusCluster,
      feedFilter,
      setFeedFilter,
      toast,
    }}>
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard() {
  const ctx = useContext(DashboardContext)
  if (!ctx) throw new Error('useDashboard must be used within DashboardProvider')
  return ctx
}
