"""Pydantic models for all database tables.

Each table has two models:
- *Create: For inserting new records (no id or timestamps)
- *Row: For reading from database (includes id and generated timestamps)
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


# Articles
class ArticleCreate(BaseModel):
    """Article data for insertion."""

    url: str
    title: str
    domain: str
    published_at: datetime
    tone_score: float | None = None
    language: str | None = None
    source_country: str | None = None
    raw_data: dict | None = None


class ArticleRow(ArticleCreate):
    """Article row from database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# Social Posts
class SocialPostCreate(BaseModel):
    """Social post data for insertion."""

    telegram_id: int | None = None
    channel: str
    text: str | None = None
    timestamp: datetime
    views: int | None = None
    raw_data: dict | None = None


class SocialPostRow(SocialPostCreate):
    """Social post row from database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# Vessel Positions
class VesselPositionCreate(BaseModel):
    """Vessel position data for insertion."""

    mmsi: int
    ship_name: str | None = None
    latitude: float
    longitude: float
    speed: float | None = None
    course: float | None = None
    timestamp: datetime


class VesselPositionRow(VesselPositionCreate):
    """Vessel position row from database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# Narrative Events
class NarrativeEventCreate(BaseModel):
    """Narrative event data for insertion."""

    event_type: str
    summary: str
    confidence: float | None = None
    source_ids: list | None = None


class NarrativeEventRow(NarrativeEventCreate):
    """Narrative event row from database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    detected_at: datetime


# Movement Events
class MovementEventCreate(BaseModel):
    """Movement event data for insertion."""

    event_type: str
    vessel_mmsi: int | None = None
    location_lat: float | None = None
    location_lon: float | None = None
    description: str | None = None


class MovementEventRow(MovementEventCreate):
    """Movement event row from database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    detected_at: datetime


# Alerts
class AlertCreate(BaseModel):
    """Alert data for insertion."""

    severity: Literal["low", "medium", "high", "critical"]
    title: str
    description: str | None = None
    event_ids: list | None = None


class AlertRow(AlertCreate):
    """Alert row from database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    resolved_at: datetime | None = None


# Briefs
class BriefCreate(BaseModel):
    """Brief data for insertion."""

    title: str
    summary: str
    key_developments: list | None = None


class BriefRow(BriefCreate):
    """Brief row from database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    generated_at: datetime
