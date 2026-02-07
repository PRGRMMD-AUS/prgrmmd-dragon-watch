"""Pydantic models for correlation results and alert data.

These models structure the output of the correlation engine and prepare
data for storage in Supabase (especially JSONB columns).
"""

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class SubScores(BaseModel):
    """Component scores that contribute to composite correlation score.

    Each sub-score is 0-100 and represents a specific correlation signal.
    """

    outlet_score: float = Field(ge=0, le=100, description="State media coordination score")
    phrase_score: float = Field(ge=0, le=100, description="Synchronized messaging score")
    volume_score: float = Field(ge=0, le=100, description="Event volume anomaly score")
    geo_score: float = Field(ge=0, le=100, description="Geographic alignment score")


class CorrelationResult(BaseModel):
    """Complete correlation analysis result.

    This is the core output of the correlation engine, containing all
    evidence, scores, and metadata needed to create or update an alert.
    """

    model_config = ConfigDict(from_attributes=True)

    narrative_event_ids: list[int] = Field(description="IDs of correlated narrative events")
    movement_event_ids: list[int] = Field(description="IDs of correlated movement events")
    composite_score: float = Field(ge=0, le=100, description="Overall correlation strength (0-100)")
    sub_scores: SubScores = Field(description="Component scores")
    threat_level: str = Field(description="GREEN, AMBER, or RED")
    confidence: int = Field(ge=0, le=100, description="Confidence in correlation (0-100)")
    geo_match: bool = Field(description="Whether geographic focus matches Taiwan Strait")
    region: str = Field(default="Taiwan Strait", description="Geographic region of concern")
    evidence_summary: str = Field(
        description="Plain-English one-liner describing what triggered the correlation"
    )
    detected_at: datetime = Field(description="When this correlation was detected")


class AlertUpsertData(BaseModel):
    """Data structure for upserting alerts in Supabase.

    This model prepares correlation results for storage, flattening
    nested structures into JSONB-ready dictionaries.
    """

    model_config = ConfigDict(from_attributes=True)

    region: str = Field(description="Geographic region (e.g., 'Taiwan Strait')")
    threat_level: str = Field(description="GREEN, AMBER, or RED")
    threat_score: float = Field(ge=0, le=100, description="Composite correlation score")
    confidence: int = Field(ge=0, le=100, description="Confidence in assessment")
    sub_scores: dict = Field(
        description="JSONB dict with outlet_score, phrase_score, volume_score, geo_score"
    )
    correlation_metadata: dict = Field(
        description=(
            "JSONB dict with narrative_event_ids, movement_event_ids, "
            "evidence_summary, detection_history list"
        )
    )
    updated_at: str = Field(description="ISO format timestamp of this update")
