from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class NarrativeCoordination(BaseModel):
    coordination_score: int = Field(ge=0, le=100, description="0-100 score indicating likelihood of coordination")
    synchronized_phrases: List[str] = Field(description="List of identical or near-identical phrases found across outlets")
    outlet_count: int = Field(description="Number of distinct stats media outlets involved")
    geographic_focus: str = Field(description="Primary geographic region targeted by the narrative")
    themes: List[str] = Field(description="Key narrative themes detected")
    confidence: int = Field(ge=0, le=100, description="Confidence in the analysis")

class MovementCategory(str, Enum):
    convoy = "convoy"
    naval = "naval"
    flight = "flight"
    restricted_zone = "restricted_zone"
    not_relevant = "not_relevant"

class PostClassification(BaseModel):
    category: MovementCategory
    location: Optional[str] = None
    confidence: int = Field(ge=0, le=100)
    reasoning: str

class ExtractedEntity(BaseModel):
    entity_type: str
    entity_value: str
    source_span: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: int = Field(ge=0, le=100)

class EntityExtraction(BaseModel):
    entities: List[ExtractedEntity]

class ThreatLevel(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"

class IntelligenceBrief(BaseModel):
    threat_level: ThreatLevel
    confidence: int = Field(ge=0, le=100)
    summary: str
    evidence_chain: List[str]
    timeline: str
    information_gaps: List[str]
    collection_priorities: List[str]
