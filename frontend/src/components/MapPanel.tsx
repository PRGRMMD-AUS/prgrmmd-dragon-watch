import { useEffect, useState } from 'react'
import Map, { Marker, Source, Layer } from 'react-map-gl/mapbox'
import type { LayerProps } from 'react-map-gl/mapbox'
import 'mapbox-gl/dist/mapbox-gl.css'
import { useVesselPositions } from '../hooks/useVesselPositions'
import { useMovementHeatmap } from '../hooks/useMovementHeatmap'
import { useNarrativeRegions } from '../hooks/useNarrativeRegions'

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN

// Taiwan Strait fixed view
const INITIAL_VIEW = {
  latitude: 24.5,
  longitude: 120.0,
  zoom: 6.5,
}

// Heatmap layer configuration
const heatmapLayer: LayerProps = {
  id: 'heatmap',
  type: 'heatmap',
  paint: {
    // Increase radius
    'heatmap-radius': 20,
    // Increase intensity
    'heatmap-intensity': 1,
    // Opacity
    'heatmap-opacity': 0.6,
    // Color ramp: transparent → blue → cyan → yellow → red
    'heatmap-color': [
      'interpolate',
      ['linear'],
      ['heatmap-density'],
      0,
      'rgba(0, 0, 0, 0)',
      0.2,
      'rgb(0, 0, 255)',
      0.4,
      'rgb(0, 255, 255)',
      0.6,
      'rgb(255, 255, 0)',
      0.8,
      'rgb(255, 128, 0)',
      1,
      'rgb(255, 0, 0)',
    ],
  },
}

// Narrative region fill layer configuration
const regionFillLayer: LayerProps = {
  id: 'region-fill',
  type: 'fill',
  paint: {
    'fill-color': 'rgba(147, 51, 234, 0.15)', // Purple tint
    'fill-outline-color': 'rgba(147, 51, 234, 0.4)',
  },
}

// Vessel marker icon (triangle/arrow)
function VesselMarker({
  course,
  isPinging,
}: {
  course: number | null
  isPinging: boolean
}) {
  const rotation = course || 0

  return (
    <div
      className={`${isPinging ? 'animate-ping' : ''}`}
      style={{
        transform: `rotate(${rotation}deg)`,
        width: '16px',
        height: '16px',
      }}
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M8 2 L14 14 L8 11 L2 14 Z" fill="#2563eb" stroke="#1e40af" strokeWidth="1" />
      </svg>
    </div>
  )
}

// Fallback map (no Mapbox token)
function FallbackMap() {
  return (
    <div className="w-full h-full bg-slate-50 flex items-center justify-center">
      <div className="text-center">
        <svg
          width="400"
          height="300"
          viewBox="117 22 5 4"
          className="mx-auto mb-4 border border-slate-200"
        >
          <rect x="117" y="22" width="5" height="4" fill="#f1f5f9" />
          {/* Simple Taiwan outline */}
          <ellipse cx="121" cy="23.8" rx="0.3" ry="0.5" fill="#94a3b8" />
          {/* Strait waters */}
          <rect x="117.5" y="22.5" width="3" height="3" fill="#bfdbfe" opacity="0.3" />
        </svg>
        <div className="text-sm text-slate-600">
          Map: Set <code className="bg-slate-100 px-1 rounded">VITE_MAPBOX_TOKEN</code> for Mapbox
        </div>
      </div>
    </div>
  )
}

export function MapPanel() {
  const { vessels, loading: vesselsLoading } = useVesselPositions()
  const { heatmapPoints, loading: heatmapLoading } = useMovementHeatmap()
  const { activeRegions, loading: regionsLoading } = useNarrativeRegions()

  // Track newly updated vessels for ping animation
  const [pingingVessels, setPingingVessels] = useState<Set<string>>(new Set())

  // Trigger ping animation when vessels update
  useEffect(() => {
    if (!vesselsLoading && vessels.size > 0) {
      // Simple approach: just track vessel count changes
      // In production, you'd compare timestamps
      const newPinging = new Set<string>()
      vessels.forEach((vessel) => {
        // Brief ping on any update (simplified)
        if (Math.random() < 0.1) {
          // Randomly ping 10% on updates
          newPinging.add(vessel.mmsi)
        }
      })

      if (newPinging.size > 0) {
        setPingingVessels(newPinging)
        setTimeout(() => setPingingVessels(new Set()), 1000)
      }
    }
  }, [vessels.size, vesselsLoading])

  // If no Mapbox token, render fallback
  if (!MAPBOX_TOKEN) {
    return <FallbackMap />
  }

  // Convert heatmap points to GeoJSON
  const heatmapGeoJSON = {
    type: 'FeatureCollection' as const,
    features: heatmapPoints.map((point) => ({
      type: 'Feature' as const,
      geometry: {
        type: 'Point' as const,
        coordinates: [point.lon, point.lat],
      },
      properties: {
        type: point.type,
      },
    })),
  }

  return (
    <div className="w-full h-full relative" style={{ gridArea: '2 / 2 / 3 / 3' }}>
      <Map
        {...INITIAL_VIEW}
        mapStyle="mapbox://styles/mapbox/light-v11"
        mapboxAccessToken={MAPBOX_TOKEN}
        scrollZoom={false}
        dragPan={false}
        dragRotate={false}
        doubleClickZoom={false}
        touchZoomRotate={false}
        style={{ width: '100%', height: '100%' }}
      >
        {/* Heatmap layer (below everything) */}
        {heatmapPoints.length > 0 && (
          <Source type="geojson" data={heatmapGeoJSON}>
            <Layer {...heatmapLayer} beforeId="waterway-label" />
          </Source>
        )}

        {/* Narrative regions (above heatmap, below vessels) */}
        {activeRegions.map((region, idx) => {
          const regionGeoJSON = {
            type: 'Feature' as const,
            geometry: {
              type: 'Polygon' as const,
              coordinates: [region.polygon],
            },
            properties: {
              name: region.name,
              eventCount: region.eventCount,
            },
          }

          return (
            <Source key={`region-${idx}`} type="geojson" data={regionGeoJSON}>
              <Layer {...regionFillLayer} id={`region-fill-${idx}`} />
            </Source>
          )
        })}

        {/* Vessel markers (on top) */}
        {Array.from(vessels.values()).map((vessel) => (
          <Marker
            key={vessel.mmsi}
            latitude={vessel.latitude}
            longitude={vessel.longitude}
            anchor="center"
          >
            <div
              title={`${vessel.ship_name || 'Unknown'} | Speed: ${vessel.speed?.toFixed(1) || 'N/A'} kts | Course: ${vessel.course?.toFixed(0) || 'N/A'}°`}
            >
              <VesselMarker
                course={vessel.course}
                isPinging={pingingVessels.has(vessel.mmsi)}
              />
            </div>
          </Marker>
        ))}
      </Map>

      {/* Loading overlay */}
      {vesselsLoading && (
        <div className="absolute top-4 left-4 bg-white px-3 py-1 rounded shadow text-xs text-slate-600">
          Loading vessels...
        </div>
      )}
    </div>
  )
}
