import asyncio
import sys
import structlog
from pydantic import ValidationError

# Configure structlog for console output
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger()

async def verify_phase_2():
    logger.info("verification_start", phase="2")
    failures = []

    # 1. Configuration & Settings
    try:
        from src.config.settings import get_settings
        settings = get_settings()
        logger.info("config_ok", claude_model=settings.claude_model, openai_model=settings.openai_model)
    except Exception as e:
        failures.append(f"Config Error: {e}")
        logger.error("config_failed", error=str(e))

    # 2. Schema Validation (LLM Outputs)
    try:
        from src.llm.schemas import (
            NarrativeCoordination, PostClassification, EntityExtraction, 
            IntelligenceBrief, ExtractedEntity
        )
        # Instantiate with dummy data to check Pydantic validation
        NarrativeCoordination(
            coordination_score=85,
            synchronized_phrases=["phrase 1", "phrase 2"],
            outlet_count=5,
            geographic_focus="Taiwan Strait",
            themes=["Theme A"],
            confidence=90
        )
        logger.info("schema_narrative_ok")
        
        # Check PostClassification
        from src.llm.schemas import MovementCategory
        PostClassification(
            category=MovementCategory.convoy,
            location="Fuzhou",
            confidence=80,
            reasoning="Convoy spotted"
        )
        logger.info("schema_classification_ok")
        
    except ValidationError as e:
        failures.append(f"Schema Validation Error: {e}")
        logger.error("schema_validation_failed", error=str(e))
    except Exception as e:
        failures.append(f"Schema Import/Other Error: {e}")
        logger.error("schema_failed", error=str(e))

    # 3. Import Module Logic (Functions)
    try:
        from src.llm.narrative import detect_narrative_coordination
        from src.llm.classification import classify_civilian_post
        from src.llm.extraction import extract_entities
        from src.llm.briefs import generate_intelligence_brief
        logger.info("llm_modules_import_ok")
    except ImportError as e:
        failures.append(f"LLM Module Import Error: {e}")
        logger.error("llm_modules_import_failed", error=str(e))

    # 4. Import Processors
    try:
        from src.processors.batch_articles import process_article_batch
        from src.processors.batch_posts import process_post_batch
        from src.processors.brief_generator import generate_brief
        logger.info("processors_import_ok")
    except ImportError as e:
        failures.append(f"Processor Import Error: {e}")
        logger.error("processors_import_failed", error=str(e))

    # Final Report
    if failures:
        logger.error("verification_failed", failures=failures)
        sys.exit(1)
    else:
        logger.info("verification_success", status="all_systems_go")

if __name__ == "__main__":
    asyncio.run(verify_phase_2())
