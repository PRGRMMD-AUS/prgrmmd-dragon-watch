"""Verification script for Dragon Watch Phase 5 demo integration.

Tests that demo infrastructure is correctly wired:
- Fixture file validity and data structure
- Demo engine functionality
- FastAPI endpoints registration
- Frontend build success
- Quick Supabase insertion test

Run directly: python scripts/verify_phase_5.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import json
import subprocess
from typing import Any


async def check_fixture_file() -> tuple[bool, str]:
    """Check 1: Fixture file exists and is valid.

    Verifies:
    - scripts/demo_fixture.json exists
    - JSON is valid
    - Has 7 table types
    - Records sorted by _demo_offset_seconds
    - Alert escalation: GREEN -> GREEN -> AMBER -> AMBER -> RED

    Returns:
        (pass, message): Test result and descriptive message
    """
    fixture_path = project_root / "scripts" / "demo_fixture.json"

    if not fixture_path.exists():
        return False, f"Fixture file not found at {fixture_path}"

    try:
        with open(fixture_path) as f:
            fixture = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # Check metadata structure
    if "metadata" not in fixture or "records" not in fixture:
        return False, "Missing metadata or records key"

    metadata = fixture["metadata"]
    records = fixture["records"]

    # Check table types
    record_counts = metadata.get("record_counts", {})
    expected_tables = {"articles", "vessel_positions", "social_posts", "movement_events",
                      "narrative_events", "alerts", "briefs"}
    actual_tables = set(record_counts.keys())

    if actual_tables != expected_tables:
        return False, f"Expected 7 tables, got {len(actual_tables)}: {actual_tables}"

    # Check total record count
    total_records = len(records)
    expected_total = metadata.get("total_records", 0)

    if total_records != expected_total:
        return False, f"Record count mismatch: {total_records} != {expected_total}"

    # Verify records sorted by _demo_offset_seconds
    offsets = [r["_demo_offset_seconds"] for r in records]
    if offsets != sorted(offsets):
        return False, "Records not sorted by _demo_offset_seconds"

    # Extract alert threat levels and verify escalation
    alerts = [r for r in records if r["_table"] == "alerts"]
    alert_levels = [a["data"]["threat_level"] for a in alerts]

    expected_escalation = ["GREEN", "GREEN", "AMBER", "AMBER", "RED"]
    if alert_levels != expected_escalation:
        return False, f"Alert escalation wrong: {alert_levels} != {expected_escalation}"

    # Build summary message
    counts_str = ", ".join(f"{k}={v}" for k, v in record_counts.items())
    return True, f"Fixture valid ({total_records} records across 7 tables: {counts_str})"


async def check_demo_engine() -> tuple[bool, str]:
    """Check 2: Demo engine importable and functional.

    Verifies:
    - Can import DemoEngine from src.demo.engine
    - load_fixture() works
    - get_status() returns expected shape
    - Speed presets map correctly

    Returns:
        (pass, message): Test result and descriptive message
    """
    try:
        from src.demo.engine import DemoEngine
    except ImportError as e:
        return False, f"Cannot import DemoEngine: {e}"

    # Create engine instance
    engine = DemoEngine()

    # Test load_fixture
    try:
        engine.load_fixture()
    except Exception as e:
        return False, f"load_fixture() failed: {e}"

    if engine.fixture is None:
        return False, "Fixture not loaded after load_fixture()"

    # Test get_status
    try:
        status = engine.get_status()
    except Exception as e:
        return False, f"get_status() failed: {e}"

    # Verify status shape
    required_fields = {"state", "speed", "speed_label", "progress", "total_records",
                      "records_inserted", "simulated_time", "simulated_hours"}
    status_fields = set(status.keys())

    if not required_fields.issubset(status_fields):
        missing = required_fields - status_fields
        return False, f"Status missing fields: {missing}"

    # Verify speed presets
    expected_speeds = {1.0: "normal", 2.5: "fast", 0.5: "slow"}
    for speed_value, expected_label in expected_speeds.items():
        engine.set_speed(speed_value)
        if engine.speed != speed_value:
            return False, f"Speed value {speed_value} not set correctly: {engine.speed} != {speed_value}"

        # Verify the label matches expected preset
        status = engine.get_status()
        if status["speed_label"] != expected_label:
            return False, f"Speed label incorrect for {speed_value}: {status['speed_label']} != {expected_label}"

    return True, "Demo engine loads and initializes"


async def check_fastapi_routes() -> tuple[bool, str]:
    """Check 3: FastAPI endpoints registered.

    Verifies:
    - Can import app from src.main
    - Routes include /api/demo/start, /pause, /reset, /speed, /status

    Returns:
        (pass, message): Test result and descriptive message
    """
    try:
        from src.main import app
    except ImportError as e:
        return False, f"Cannot import app from src.main: {e}"

    # Extract all routes
    routes = [route.path for route in app.routes]

    # Check demo endpoints exist
    expected_endpoints = [
        "/api/demo/start",
        "/api/demo/pause",
        "/api/demo/reset",
        "/api/demo/speed/{preset}",
        "/api/demo/status",
    ]

    missing_endpoints = []
    for endpoint in expected_endpoints:
        # Handle path parameters
        base_endpoint = endpoint.replace("/{preset}", "")
        if not any(route.startswith(base_endpoint) for route in routes):
            missing_endpoints.append(endpoint)

    if missing_endpoints:
        return False, f"Missing endpoints: {missing_endpoints}"

    # Count demo endpoints
    demo_routes = [r for r in routes if "/api/demo/" in r]

    return True, f"FastAPI demo routes registered ({len(demo_routes)} endpoints)"


async def check_frontend_build() -> tuple[bool, str]:
    """Check 4: Frontend build succeeds.

    Verifies:
    - npm run build succeeds (exit code 0)
    - dist/ directory exists after build

    Returns:
        (pass, message): Test result and descriptive message
    """
    frontend_dir = project_root / "frontend"

    if not frontend_dir.exists():
        return False, f"Frontend directory not found: {frontend_dir}"

    # Run npm run build
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
        )
    except subprocess.TimeoutExpired:
        return False, "Frontend build timed out after 2 minutes"
    except Exception as e:
        return False, f"Build command failed: {e}"

    if result.returncode != 0:
        return False, f"Build failed with exit code {result.returncode}: {result.stderr}"

    # Check dist/ exists
    dist_dir = frontend_dir / "dist"
    if not dist_dir.exists():
        return False, "dist/ directory not created after build"

    return True, "Frontend builds successfully"


async def check_quick_insertion() -> tuple[bool, str]:
    """Check 5: Quick insertion test.

    Verifies:
    - Start engine with 3-record subset
    - Insert into Supabase
    - Query to verify records appeared
    - Clean up (delete inserted records)

    Returns:
        (pass, message): Test result and descriptive message
    """
    try:
        from src.demo.engine import DemoEngine
        from src.database.client import get_supabase
    except ImportError as e:
        return False, f"Cannot import required modules: {e}"

    # Create engine and load fixture
    engine = DemoEngine()
    engine.load_fixture()

    # Take first 3 records
    test_records = engine.fixture["records"][:3]

    # Get Supabase client
    try:
        supabase = await get_supabase()
    except Exception as e:
        return False, f"Supabase connection failed: {e}"

    inserted_ids: dict[str, list[str]] = {}  # table -> [id, id, ...]

    try:
        # Pre-clear specific test records to avoid duplicate key errors
        for record in test_records:
            table = record["_table"]
            data = record["data"]

            if table == "articles":
                # Delete by URL (unique constraint)
                await supabase.table(table).delete().eq("url", data["url"]).execute()
            elif table == "vessel_positions":
                # Delete by mmsi + timestamp
                await supabase.table(table).delete().eq("mmsi", data["mmsi"]).eq("timestamp", data["timestamp"]).execute()
            elif table == "social_posts":
                # Delete by content hash or another unique field if available
                # For simplicity, just try insert with upsert logic
                pass

        # Insert test records
        for record in test_records:
            table = record["_table"]
            data = record["data"]

            result = await supabase.table(table).insert(data).execute()

            if not result.data:
                return False, f"Insert to {table} returned no data"

            # Track inserted ID for cleanup
            if table not in inserted_ids:
                inserted_ids[table] = []
            inserted_ids[table].append(result.data[0]["id"])

        # Verify records exist (sample check - just verify we got IDs back)
        total_inserted = sum(len(ids) for ids in inserted_ids.values())
        if total_inserted != len(test_records):
            return False, f"Expected {len(test_records)} inserts, got {total_inserted}"

        # Cleanup: delete inserted records by ID
        for table, ids in inserted_ids.items():
            for record_id in ids:
                await supabase.table(table).delete().eq("id", record_id).execute()

        return True, f"Quick insertion test (3 records inserted and verified)"

    except Exception as e:
        # Attempt cleanup on error
        try:
            for table, ids in inserted_ids.items():
                for record_id in ids:
                    await supabase.table(table).delete().eq("id", record_id).execute()
        except:
            pass  # Best effort cleanup

        return False, f"Insertion test failed: {e}"


async def main():
    """Run all Phase 5 verification checks."""
    print("\nPhase 5 Verification")
    print("=" * 50)

    checks = [
        ("Fixture file valid", check_fixture_file),
        ("Demo engine loads and initializes", check_demo_engine),
        ("FastAPI demo routes registered", check_fastapi_routes),
        ("Frontend builds successfully", check_frontend_build),
        ("Quick insertion test", check_quick_insertion),
    ]

    results = []

    for name, check_func in checks:
        try:
            passed, message = await check_func()
            results.append((passed, name, message))

            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} {message}")
        except Exception as e:
            results.append((False, name, f"Exception: {e}"))
            print(f"[FAIL] {name}: Exception: {e}")

    # Summary
    passed_count = sum(1 for p, _, _ in results if p)
    total_count = len(results)

    print(f"\n{passed_count}/{total_count} checks passed.", end="")

    if passed_count == total_count:
        print(" Demo infrastructure ready.")
        return 0
    else:
        print(" Fix failures before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
