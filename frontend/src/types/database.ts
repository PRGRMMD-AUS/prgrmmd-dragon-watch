// Database types mirroring Supabase schema

export type ThreatLevel = 'GREEN' | 'AMBER' | 'RED'

export interface Article {
  id: string
  url: string
  title: string
  domain: string
  published_at: string
  tone_score: number | null
  language: string | null
  source_country: string | null
  created_at: string
}

export interface SocialPost {
  id: string
  telegram_id: string
  channel: string
  text: string
  timestamp: string
  views: number | null
  created_at: string
}

export interface VesselPosition {
  id: string
  mmsi: string
  ship_name: string | null
  latitude: number
  longitude: number
  speed: number | null
  course: number | null
  timestamp: string
  created_at: string
}

export interface NarrativeEvent {
  id: string
  event_type: string
  summary: string
  confidence: number
  source_ids: string[]
  detected_at: string
}

export interface MovementEvent {
  id: string
  event_type: string
  vessel_mmsi: string
  location_lat: number
  location_lon: number
  description: string
  detected_at: string
}

export interface Alert {
  id: string
  severity: string
  title: string
  description: string
  event_ids: string[]
  created_at: string
  resolved_at: string | null
  region: string | null
  threat_level: ThreatLevel | null
  threat_score: number | null
  confidence: number | null
  sub_scores: Record<string, number> | null
  correlation_metadata: Record<string, any> | null
  updated_at: string | null
}

export interface Brief {
  id: string
  title: string
  summary: string
  key_developments: string[]
  generated_at: string
  threat_level: ThreatLevel | null
  confidence: number | null
  evidence_chain: Record<string, any> | null
  timeline: Record<string, any> | null
  information_gaps: string[] | null
  collection_priorities: string[] | null
  narrative_event_ids: string[] | null
  movement_event_ids: string[] | null
}
