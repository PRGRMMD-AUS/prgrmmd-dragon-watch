import { useMemo, useState, useCallback, useRef, useEffect } from 'react'
import Map, { Marker, Popup, Source, Layer } from 'react-map-gl/mapbox'
import type { MapRef, LayerProps } from 'react-map-gl/mapbox'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Plus, Minus, AlertTriangle, X, Eye, ExternalLink, Play, Pause, RotateCcw } from 'lucide-react'
import { useVesselPositions } from '../hooks/useVesselPositions'
import { useMovementHeatmap } from '../hooks/useMovementHeatmap'
import { useDemoControl } from '../hooks/useDemoControl'
import type { HeatmapPoint } from '../hooks/useMovementHeatmap'
import { useDashboard } from '../context/DashboardContext'

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN

const VESSEL_STYLES = {
  high: { fill: '#e05a4f', stroke: '#8a3530', size: 12 },
  medium: { fill: '#a3a3a3', stroke: '#666666', size: 9 },
  low: { fill: '#4a4a4a', stroke: '#333333', size: 7 },
} as const

type Importance = keyof typeof VESSEL_STYLES

const LINE_COLORS: Record<string, string> = {
  speed_anomaly: '#ef4444',
  formation_change: '#a78bfa',
  zone_entry: '#f97316',
  course_deviation: '#38bdf8',
}
const DEFAULT_LINE_COLOR = '#6b7280'

const EVENT_DOT_COLORS: Record<string, string> = {
  speed_anomaly: '#ef4444',
  formation_change: '#a78bfa',
  zone_entry: '#f97316',
  course_deviation: '#38bdf8',
}
const DEFAULT_EVENT_DOT_COLOR = '#6b7280'

const SPEED_PRESETS = [1, 2, 5, 10, 25] as const

function VesselDot({ importance }: { importance: Importance }) {
  const style = VESSEL_STYLES[importance]
  return (
    <svg width={style.size} height={style.size} viewBox={`0 0 ${style.size} ${style.size}`}>
      <circle cx={style.size / 2} cy={style.size / 2} r={style.size / 2 - 0.5} fill={style.fill} stroke={style.stroke} strokeWidth={0.5} />
    </svg>
  )
}

function EventDot({ color, selected, escalated, dimmed }: { color: string; selected?: boolean; escalated?: boolean; dimmed?: boolean }) {
  const size = selected ? 16 : 10
  const half = size / 2
  const dotColor = dimmed ? '#555555' : color
  const dotOpacity = dimmed ? 0.4 : 0.85
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {selected && (
        <circle cx={half} cy={half} r={half - 1} fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth={0.5} strokeDasharray="2 2" />
      )}
      <circle cx={half} cy={half} r={selected ? 5 : 4} fill={dotColor} fillOpacity={dotOpacity} stroke={dotColor} strokeWidth={0.5} strokeOpacity={dimmed ? 0.3 : 1} />
      <circle cx={half} cy={half} r={selected ? 2.5 : 1.5} fill="white" fillOpacity={dimmed ? 0.15 : 0.4} />
      {escalated && !dimmed && (
        <circle cx={size - 2} cy={2} r={1.5} fill="#e05a4f" />
      )}
    </svg>
  )
}

function FallbackMap() {
  return (
    <div className="w-full h-full bg-[var(--bg-base)] flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border border-[var(--border-glass)] mx-auto mb-4 flex items-center justify-center">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" className="text-[var(--text-dim)]">
            <circle cx="12" cy="12" r="10" />
            <line x1="2" y1="12" x2="22" y2="12" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
        </div>
        <div className="text-[10px] text-[var(--text-dim)] font-mono uppercase tracking-wider">Set VITE_MAPBOX_TOKEN</div>
      </div>
    </div>
  )
}

function formatEventTime(detected_at: string): string {
  const d = new Date(detected_at)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const DENSITY_PRESETS = [
  { label: 'Low', radius: 25, intensity: 0.8 },
  { label: 'Med', radius: 40, intensity: 1.5 },
  { label: 'High', radius: 60, intensity: 2.5 },
] as const

export function MapPanel() {
  const mapRef = useRef<MapRef>(null)
  const { vessels, importantVessels, loading: vesselsLoading } = useVesselPositions()
  const { heatmapPoints, clusters, pointClusterMap } = useMovementHeatmap()
  const { status, start, pause, reset, setSpeedMultiplier, error: demoError } = useDemoControl()
  const [densityLevel, setDensityLevel] = useState(1)
  const [speedIndex, setSpeedIndex] = useState(0)
  const [viewState, setViewState] = useState({
    latitude: 24.5,
    longitude: 120.0,
    zoom: 6.5,
  })

  const {
    selectedMovementEventId,
    selectFromMap,
    popupPoint,
    setPopupPoint,
    narrativeFilter,
    setNarrativeFilter,
    timelinePosition,
    setTimelinePosition,
    escalatedIds,
    escalateEvent,
    startEscalation,
    focusCluster,
    setFocusCluster,
  } = useDashboard()

  // Fly to selected event when a card is clicked
  useEffect(() => {
    if (!selectedMovementEventId) return
    const point = heatmapPoints.find(p => p.id === selectedMovementEventId)
    if (!point) return
    mapRef.current?.flyTo({
      center: [point.lon, point.lat],
      zoom: Math.max(viewState.zoom, 8),
      duration: 1200,
    })
    setPopupPoint(point)
  }, [selectedMovementEventId]) // eslint-disable-line react-hooks/exhaustive-deps

  const density = DENSITY_PRESETS[densityLevel]

  const isPlaying = status?.state === 'playing'
  const isIdle = status?.state === 'idle'
  const isPaused = status?.state === 'paused'
  const demoDisabled = !!demoError || !status

  const handlePlayPause = () => {
    if (isPlaying) pause()
    else if (isIdle) start(true)
    else if (isPaused) start(false)
  }

  const handleCycleSpeed = () => {
    const nextIndex = (speedIndex + 1) % SPEED_PRESETS.length
    setSpeedIndex(nextIndex)
    setSpeedMultiplier(SPEED_PRESETS[nextIndex])
  }

  // Set of point IDs in the focused cluster
  const focusPointIds = useMemo(() => {
    if (!focusCluster) return null
    return new Set(focusCluster.points.map(p => p.id))
  }, [focusCluster])

  // Filter points by narrative filter, timeline position, and cluster focus
  const visiblePoints = useMemo(() => {
    let pts = heatmapPoints
    if (focusPointIds) {
      return pts.filter(p => focusPointIds.has(p.id))
    }
    if (narrativeFilter) {
      pts = pts.filter(p => p.type === narrativeFilter)
    }
    if (timelinePosition < 100 && pts.length > 0) {
      const maxIndex = Math.max(1, Math.ceil((timelinePosition / 100) * pts.length))
      pts = pts.slice(0, maxIndex)
    }
    return pts
  }, [heatmapPoints, narrativeFilter, timelinePosition, focusPointIds])

  // Time range labels
  const timeRange = useMemo(() => {
    if (heatmapPoints.length === 0) return { start: '--:--', end: '--:--' }
    return {
      start: formatEventTime(heatmapPoints[0].detected_at),
      end: formatEventTime(heatmapPoints[heatmapPoints.length - 1].detected_at),
    }
  }, [heatmapPoints])

  const heatmapLayer: LayerProps = useMemo(
    () => ({
      id: 'heatmap',
      type: 'heatmap',
      paint: {
        'heatmap-radius': density.radius,
        'heatmap-intensity': density.intensity,
        'heatmap-opacity': focusCluster ? 0.15 : 0.45,
        'heatmap-color': [
          'interpolate', ['linear'], ['heatmap-density'],
          0, 'rgba(0, 0, 0, 0)',
          0.2, 'rgba(224, 90, 79, 0.15)',
          0.5, 'rgba(224, 90, 79, 0.35)',
          0.8, 'rgba(255, 160, 120, 0.5)',
          1, 'rgba(255, 220, 180, 0.6)',
        ],
      },
    }),
    [density, focusCluster],
  )

  const handleDotClick = useCallback((point: HeatmapPoint, e: React.MouseEvent) => {
    e.stopPropagation()
    if (popupPoint?.id === point.id) {
      setPopupPoint(null)
    } else {
      setPopupPoint(point)
    }
  }, [popupPoint, setPopupPoint])

  const handlePopupViewInFeed = useCallback(() => {
    if (popupPoint) {
      selectFromMap(popupPoint.id)
    }
  }, [popupPoint, selectFromMap])

  const handleFocusCluster = useCallback((pointId: string) => {
    const clusterId = pointClusterMap[pointId]
    if (!clusterId) return
    const cluster = clusters.find(c => c.id === clusterId)
    if (cluster) {
      setFocusCluster(cluster)
      setPopupPoint(null)
    }
  }, [pointClusterMap, clusters, setFocusCluster, setPopupPoint])

  const handleEscalateFromPopup = useCallback(() => {
    if (popupPoint) {
      startEscalation({
        eventId: popupPoint.id,
        eventType: popupPoint.type,
        description: popupPoint.description || `${popupPoint.type.replace(/_/g, ' ')} at ${popupPoint.lat.toFixed(2)}°N ${popupPoint.lon.toFixed(2)}°E`,
      })
    }
  }, [popupPoint, startEscalation])

  if (!MAPBOX_TOKEN) return <FallbackMap />

  const heatmapGeoJSON = {
    type: 'FeatureCollection' as const,
    features: visiblePoints.map((point) => ({
      type: 'Feature' as const,
      geometry: { type: 'Point' as const, coordinates: [point.lon, point.lat] },
      properties: { type: point.type },
    })),
  }

  // Connection lines
  const connectionLines = (() => {
    if (focusCluster) {
      const points = focusCluster.points
      if (points.length < 2) return { type: 'FeatureCollection' as const, features: [] as GeoJSON.Feature[] }
      return {
        type: 'FeatureCollection' as const,
        features: [{
          type: 'Feature' as const,
          geometry: { type: 'LineString' as const, coordinates: points.map(p => [p.lon, p.lat]) },
          properties: { event_type: focusCluster.type, color: LINE_COLORS[focusCluster.type] || DEFAULT_LINE_COLOR },
        }],
      }
    }
    const grouped: Record<string, { lon: number; lat: number }[]> = {}
    for (const pt of visiblePoints) {
      if (!grouped[pt.type]) grouped[pt.type] = []
      grouped[pt.type].push({ lon: pt.lon, lat: pt.lat })
    }
    const features: GeoJSON.Feature[] = []
    for (const [type, points] of Object.entries(grouped)) {
      if (points.length < 2) continue
      features.push({
        type: 'Feature',
        geometry: { type: 'LineString', coordinates: points.map((p) => [p.lon, p.lat]) },
        properties: { event_type: type, color: LINE_COLORS[type] || DEFAULT_LINE_COLOR },
      })
    }
    return { type: 'FeatureCollection' as const, features }
  })()

  const hasIndividualSelection = !!focusCluster && !!selectedMovementEventId

  const connectionLineLayer: LayerProps = {
    id: 'connection-lines',
    type: 'line',
    paint: {
      'line-color': hasIndividualSelection ? '#555555' : ['get', 'color'],
      'line-width': focusCluster ? 1.5 : 1,
      'line-opacity': hasIndividualSelection ? 0.15 : focusCluster ? 0.7 : 0.4,
      'line-dasharray': [6, 4],
    },
  }

  const handleZoomIn = () => setViewState(vs => ({ ...vs, zoom: Math.min(vs.zoom + 1, 18) }))
  const handleZoomOut = () => setViewState(vs => ({ ...vs, zoom: Math.max(vs.zoom - 1, 2) }))

  return (
    <div className="w-full h-full relative">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        onClick={() => { setPopupPoint(null); if (focusCluster) { setFocusCluster(null); setNarrativeFilter(null) } }}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={MAPBOX_TOKEN}
        attributionControl={false}
        style={{ width: '100%', height: '100%' }}
      >
        {visiblePoints.length > 0 && (
          <Source type="geojson" data={heatmapGeoJSON}>
            <Layer {...heatmapLayer} beforeId="waterway-label" />
          </Source>
        )}

        {connectionLines.features.length > 0 && (
          <Source type="geojson" data={connectionLines}>
            <Layer {...connectionLineLayer} />
          </Source>
        )}

        {/* Event dots — large click target wrapping visible SVG */}
        {visiblePoints.map((point) => {
          const isSelected = selectedMovementEventId === point.id
          const isDimmed = !!focusCluster && !!selectedMovementEventId && !isSelected
          return (
            <Marker
              key={`event-${point.id}`}
              latitude={point.lat}
              longitude={point.lon}
              anchor="center"
            >
              <div
                className="cursor-pointer flex items-center justify-center"
                style={{ width: 28, height: 28 }}
                onClick={(e) => handleDotClick(point, e)}
              >
                <EventDot
                  color={EVENT_DOT_COLORS[point.type] || DEFAULT_EVENT_DOT_COLOR}
                  selected={isSelected}
                  escalated={escalatedIds.has(point.id)}
                  dimmed={isDimmed}
                />
              </div>
            </Marker>
          )
        })}

        {/* Vessel markers — hidden in cluster focus */}
        {!focusCluster && Array.from(vessels.values()).map((vessel) => {
          const importance: Importance = importantVessels.has(vessel.mmsi)
            ? 'high'
            : (vessel.speed ?? 0) > 15 ? 'medium' : 'low'
          return (
            <Marker key={vessel.mmsi} latitude={vessel.latitude} longitude={vessel.longitude} anchor="center">
              <div title={`${vessel.ship_name || 'Unknown'} | ${vessel.speed?.toFixed(1) || '?'} kts`}>
                <VesselDot importance={importance} />
              </div>
            </Marker>
          )
        })}

        {/* Popup — appears next to clicked dot */}
        {popupPoint && (
          <Popup
            latitude={popupPoint.lat}
            longitude={popupPoint.lon}
            anchor="left"
            offset={16}
            closeButton={false}
            closeOnClick={false}
            className="map-popup"
          >
            <div className="min-w-[180px] max-w-[220px]">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full" style={{ background: EVENT_DOT_COLORS[popupPoint.type] || DEFAULT_EVENT_DOT_COLOR }} />
                  <span className="text-[10px] font-mono text-[var(--text-primary)] uppercase tracking-wider">
                    {popupPoint.type.replace(/_/g, ' ')}
                  </span>
                </div>
                <button onClick={() => setPopupPoint(null)} className="text-[var(--text-dim)] hover:text-[var(--text-muted)] ml-2">
                  <X size={10} />
                </button>
              </div>

              {popupPoint.description && (
                <p className="text-[10px] text-[var(--text-secondary)] leading-[1.4] mb-1.5 line-clamp-3">
                  {popupPoint.description}
                </p>
              )}

              <div className="flex items-center gap-2 text-[9px] font-mono text-[var(--text-dim)] tabular-nums mb-2">
                <span>{popupPoint.vessel_mmsi}</span>
                <span>{popupPoint.lat.toFixed(2)}°N {popupPoint.lon.toFixed(2)}°E</span>
                <span>{formatEventTime(popupPoint.detected_at)}</span>
              </div>

              <div className="flex flex-col gap-1">
                <button
                  onClick={handlePopupViewInFeed}
                  className="flex items-center gap-1.5 w-full px-2 py-1 text-[9px] font-mono uppercase tracking-wider text-[var(--text-muted)] border border-[var(--border-subtle)] hover:text-[var(--text-primary)] hover:border-[var(--border-glass)] transition-colors"
                >
                  <ExternalLink size={8} /> View in feed
                </button>

                {pointClusterMap[popupPoint.id] && !focusCluster && (
                  <button
                    onClick={() => handleFocusCluster(popupPoint.id)}
                    className="flex items-center gap-1.5 w-full px-2 py-1 text-[9px] font-mono uppercase tracking-wider text-[var(--text-muted)] border border-[var(--border-subtle)] hover:text-[var(--text-primary)] hover:border-[var(--border-glass)] transition-colors"
                  >
                    <Eye size={8} /> Show cluster ({clusters.find(c => c.id === pointClusterMap[popupPoint.id])?.points.length} events)
                  </button>
                )}

                {!escalatedIds.has(popupPoint.id) ? (
                  <button
                    onClick={handleEscalateFromPopup}
                    className="flex items-center gap-1.5 w-full px-2 py-1 text-[9px] font-mono uppercase tracking-wider text-[var(--accent)] border border-[var(--accent-dim)] hover:bg-[var(--accent-dim)] transition-colors"
                  >
                    <AlertTriangle size={8} /> Escalate
                  </button>
                ) : (
                  <div className="flex items-center gap-1.5 px-2 py-1 text-[9px] font-mono text-[var(--accent)] uppercase tracking-wider">
                    <AlertTriangle size={8} /> Escalated
                  </div>
                )}
              </div>
            </div>
          </Popup>
        )}
      </Map>

      {/* Zoom controls */}
      <div className="absolute top-3 left-3 flex flex-col gap-[1px]">
        <button onClick={handleZoomIn} className="glass-strong w-7 h-7 flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
          <Plus size={12} />
        </button>
        <button onClick={handleZoomOut} className="glass-strong w-7 h-7 flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
          <Minus size={12} />
        </button>
      </div>

      {/* Cluster focus banner */}
      {focusCluster && (
        <div className="absolute top-3 left-12 right-3 glass-strong px-3 py-2 flex items-center gap-3 animate-fadeUp">
          <div className="w-2 h-2 rounded-full" style={{ background: EVENT_DOT_COLORS[focusCluster.type] || DEFAULT_EVENT_DOT_COLOR }} />
          <span className="text-[10px] font-mono text-[var(--text-primary)] uppercase tracking-wider">
            {focusCluster.type.replace(/_/g, ' ')} cluster
          </span>
          <span className="text-[10px] font-mono text-[var(--text-dim)] tabular-nums">
            {focusCluster.points.length} events
          </span>
          <button
            onClick={() => setFocusCluster(null)}
            className="ml-auto flex items-center gap-1 text-[10px] font-mono text-[var(--text-dim)] hover:text-[var(--text-muted)] uppercase tracking-wider"
          >
            <X size={9} /> Exit
          </button>
        </div>
      )}

      {/* Density control */}
      {!focusCluster && (
        <div className="absolute top-3 right-3 glass-strong px-2 py-1 flex items-center gap-1 text-[10px]">
          <span className="text-[var(--text-dim)] font-mono uppercase tracking-wider mr-1">Density</span>
          {DENSITY_PRESETS.map((preset, i) => (
            <button
              key={preset.label}
              onClick={() => setDensityLevel(i)}
              className={`px-1.5 py-0.5 font-mono uppercase tracking-wider transition-all duration-150 ${
                densityLevel === i
                  ? 'text-[var(--text-primary)] border border-[var(--border-active)]'
                  : 'text-[var(--text-dim)] hover:text-[var(--text-muted)] border border-transparent'
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>
      )}

      {/* Cluster list overlay */}
      {!focusCluster && clusters.length > 0 && (
        <div className="absolute bottom-14 left-3 glass-strong px-2 py-1.5 flex flex-col gap-1 text-[10px] max-h-32 overflow-y-auto">
          <span className="text-[var(--text-dim)] font-mono uppercase tracking-wider mb-0.5">Clusters</span>
          {clusters.slice(0, 5).map(cluster => (
            <button
              key={cluster.id}
              onClick={() => setFocusCluster(cluster)}
              className="flex items-center gap-1.5 px-1 py-0.5 text-left font-mono uppercase tracking-wider text-[var(--text-dim)] hover:text-[var(--text-muted)] transition-all duration-150"
            >
              <div className="w-2 h-2 rounded-full" style={{ background: EVENT_DOT_COLORS[cluster.type] || DEFAULT_EVENT_DOT_COLOR }} />
              <span>{cluster.type.replace(/_/g, ' ')}</span>
              <span className="text-[var(--text-dim)] tabular-nums">{cluster.points.length}</span>
            </button>
          ))}
        </div>
      )}

      {/* Timeline + playback controls — glass bar at bottom */}
      <div className="absolute bottom-0 left-0 right-0 glass-panel px-3 py-2 flex items-center gap-2">
        {/* Play/Pause */}
        <button
          onClick={handlePlayPause}
          disabled={demoDisabled}
          className="w-7 h-7 flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--text-primary)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors shrink-0"
        >
          {isPlaying ? <Pause size={12} /> : <Play size={12} />}
        </button>

        {/* Reset */}
        <button
          onClick={() => reset()}
          disabled={demoDisabled}
          className="w-7 h-7 flex items-center justify-center text-[var(--text-dim)] hover:text-[var(--text-muted)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors shrink-0"
        >
          <RotateCcw size={10} />
        </button>

        {/* Speed cycle button */}
        <button
          onClick={handleCycleSpeed}
          disabled={demoDisabled}
          className="px-1.5 py-0.5 text-[9px] font-mono text-[var(--text-muted)] border border-[var(--border-subtle)] hover:text-[var(--text-primary)] hover:border-[var(--border-glass)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors tabular-nums shrink-0 min-w-[32px] text-center"
        >
          {SPEED_PRESETS[speedIndex]}x
        </button>

        <div className="h-3 w-px bg-[var(--border-glass)] shrink-0" />

        {/* Timeline scrubber */}
        <span className="text-[9px] font-mono text-[var(--text-dim)] tabular-nums shrink-0">{timeRange.start}</span>
        <input
          type="range"
          min={0}
          max={100}
          value={timelinePosition}
          onChange={(e) => setTimelinePosition(Number(e.target.value))}
          className="timeline-scrubber flex-1 min-w-0"
        />
        <span className="text-[9px] font-mono text-[var(--text-dim)] tabular-nums shrink-0">{timeRange.end}</span>

        <div className="h-3 w-px bg-[var(--border-glass)] shrink-0" />

        {/* Simulated time */}
        <span className="text-[9px] font-mono text-[var(--text-secondary)] tabular-nums shrink-0">
          {status?.simulated_time || 'T+0h'}
        </span>
      </div>

      {vesselsLoading && (
        <div className="absolute top-3 left-12 glass-strong px-2.5 py-1 text-[10px] text-[var(--text-muted)] font-mono uppercase tracking-wider">
          Loading...
        </div>
      )}
    </div>
  )
}
