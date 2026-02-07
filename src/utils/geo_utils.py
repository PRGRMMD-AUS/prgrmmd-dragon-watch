"""Geographic utilities for Taiwan Strait region correlation.

Provides bounding box containment checks and geographic matching utilities
using Shapely for single-region analysis (no GeoPandas needed for demo).
"""

from shapely.geometry import Point, box

# Taiwan Strait bounding box (matches demo data coordinates)
# From load_demo_data.py: 23-26N, 118-122E
TAIWAN_STRAIT_BBOX = {
    "name": "Taiwan Strait",
    "lon_min": 118.0,
    "lat_min": 23.0,
    "lon_max": 122.0,
    "lat_max": 26.0,
}


def is_in_taiwan_strait(lat: float, lon: float) -> bool:
    """Check if coordinate point is within Taiwan Strait bounding box.

    Uses Shapely geometric containment for accurate boundary checking.
    Coordinate order: lon, lat (Shapely uses x, y = lon, lat).

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        True if point is within Taiwan Strait region, False otherwise
    """
    region_box = box(
        TAIWAN_STRAIT_BBOX["lon_min"],
        TAIWAN_STRAIT_BBOX["lat_min"],
        TAIWAN_STRAIT_BBOX["lon_max"],
        TAIWAN_STRAIT_BBOX["lat_max"],
    )
    point = Point(lon, lat)
    return region_box.contains(point)


def check_narrative_geo_match(geographic_focus: str | None) -> bool:
    """Check if narrative's geographic focus matches Taiwan Strait region.

    Case-insensitive substring matching for regional keywords.

    Args:
        geographic_focus: Geographic focus string from narrative event (or None)

    Returns:
        True if focus mentions Taiwan/Strait/Fujian keywords, False otherwise
    """
    if not geographic_focus:
        return False

    focus_lower = geographic_focus.lower()
    keywords = ["taiwan", "strait", "fujian"]

    return any(keyword in focus_lower for keyword in keywords)


def normalize_min_max(value: float, min_val: float, max_val: float) -> float:
    """Normalize value to 0-100 scale using min-max normalization.

    Args:
        value: Value to normalize
        min_val: Minimum value in range
        max_val: Maximum value in range

    Returns:
        Normalized value 0-100, or 50.0 if min_val == max_val (neutral)
    """
    # Handle edge case where all values are identical
    if max_val == min_val:
        return 50.0

    # Standard min-max normalization to 0-100
    normalized = ((value - min_val) / (max_val - min_val)) * 100.0

    # Clamp to 0-100 range
    return max(0.0, min(100.0, normalized))
