from typing import List, Dict

# Content Limits
NARRATIVE_MAX_ARTICLES = 20
NARRATIVE_ARTICLE_SNIPPET_LEN = 500

# Classification Categories
CLASSIFICATION_CATEGORIES: List[str] = [
    "convoy", 
    "naval", 
    "flight", 
    "restricted_zone", 
    "not_relevant"
]

# Entity Types
ENTITY_TYPES: List[str] = [
    "military_unit", 
    "equipment", 
    "location", 
    "timestamp"
]

# Threat Levels Mapping
# Score range -> Level
THREAT_LEVELS: Dict[str, tuple] = {
    "GREEN": (0, 30),
    "AMBER": (31, 70),
    "RED": (71, 100)
}
