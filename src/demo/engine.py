"""Async demo playback engine for Dragon Watch.

Reads pre-computed fixture from scripts/demo_fixture.json and drip-feeds records
into Supabase with controlled timing, causing all dashboard panels to update via
their existing realtime subscriptions.

The engine handles:
- Timing and pacing control (normal/fast/slow speed presets)
- State management (idle/playing/paused)
- Interruptible sleep for responsive pause/reset
- Table clearing before demo start
- Alert upsert pattern (first INSERT, subsequent UPDATE)
"""

import asyncio
import json
from pathlib import Path
from typing import Literal

import structlog

from src.database.client import get_supabase

logger = structlog.get_logger()


class DemoEngine:
    """Async demo playback engine for Dragon Watch.

    Manages demo playback state and Supabase insertion with controlled timing.
    Singleton pattern ensures frontend controls and engine share state.
    """

    def __init__(self):
        """Initialize demo engine with idle state."""
        self.state: Literal["idle", "playing", "paused"] = "idle"
        self.speed: float = 1.0  # 1.0 = Normal (5 min), 2.5 = Fast (2 min), 0.5 = Slow (10 min)
        self.current_index: int = 0  # Current position in fixture records
        self.fixture: dict | None = None  # Cached fixture data
        self.task: asyncio.Task | None = None  # Background playback task
        self.simulated_seconds_elapsed: float = 0.0  # Track scenario time progress
        self.alert_id: str | None = None  # Track inserted alert ID for updates
        self.records_inserted: int = 0  # Count of records inserted so far

    def load_fixture(self) -> None:
        """Load scripts/demo_fixture.json into memory on first use.

        Caches fixture data for subsequent playback runs.

        Raises:
            FileNotFoundError: If demo_fixture.json doesn't exist
            json.JSONDecodeError: If fixture JSON is malformed
        """
        if self.fixture is not None:
            logger.info("fixture_already_loaded", records=len(self.fixture["records"]))
            return

        fixture_path = Path(__file__).parent.parent.parent / "scripts" / "demo_fixture.json"

        if not fixture_path.exists():
            raise FileNotFoundError(
                f"Demo fixture not found at {fixture_path}. "
                "Run: python scripts/generate_demo_fixture.py"
            )

        with open(fixture_path) as f:
            self.fixture = json.load(f)

        logger.info(
            "fixture_loaded",
            records=len(self.fixture["records"]),
            tables=self.fixture["metadata"]["record_counts"],
        )

    async def start(self, clear_first: bool = True) -> None:
        """Start or resume playback.

        Args:
            clear_first: If True and state is "idle", clear all 7 Supabase tables before starting.
                        If state is "paused", resume without clearing.

        Behavior:
            - Idle + clear_first=True: Clear tables, reset state, start from beginning
            - Idle + clear_first=False: Start from beginning without clearing
            - Paused: Resume from current_index without clearing
            - Playing: No-op (already playing)
        """
        if self.state == "playing":
            logger.warning("start_ignored", reason="already_playing")
            return

        # Load fixture if not already loaded
        self.load_fixture()

        # Clear tables if starting fresh with clear_first=True
        if self.state == "idle" and clear_first:
            logger.info("clearing_tables_before_start")
            await self._clear_tables()
            self.current_index = 0
            self.simulated_seconds_elapsed = 0.0
            self.records_inserted = 0
            self.alert_id = None

        # Set state to playing and spawn background task
        self.state = "playing"
        self.task = asyncio.create_task(self._playback_loop())

        logger.info(
            "playback_started",
            speed=self.speed,
            speed_label=self._get_speed_label(),
            resume_index=self.current_index,
            total_records=len(self.fixture["records"]),
        )

    async def pause(self) -> None:
        """Pause playback at current position.

        Sets state to "paused". The playback loop checks state and stops iterating.
        Resume with start() to continue from current position.
        """
        if self.state != "playing":
            logger.warning("pause_ignored", reason=f"not_playing (state={self.state})")
            return

        self.state = "paused"
        logger.info(
            "playback_paused",
            current_index=self.current_index,
            simulated_time=self._format_simulated_time(),
        )

    async def reset(self) -> None:
        """Reset playback to beginning and clear all tables.

        Cancels running playback task, clears all 7 Supabase tables,
        and resets state to idle.
        """
        # Cancel playback task if running
        if self.task is not None and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None

        # Reset state
        self.state = "idle"
        self.current_index = 0
        self.simulated_seconds_elapsed = 0.0
        self.records_inserted = 0
        self.alert_id = None

        # Clear all tables
        await self._clear_tables()

        logger.info("playback_reset")

    def set_speed(self, speed: float) -> None:
        """Update speed multiplier.

        Args:
            speed: Speed multiplier (0.5 = slow, 1.0 = normal, 2.5 = fast)

        Takes effect immediately on next record's delay calculation.
        """
        old_speed = self.speed
        self.speed = speed

        logger.info(
            "speed_changed",
            old_speed=old_speed,
            new_speed=speed,
            old_label=self._get_speed_label(old_speed),
            new_label=self._get_speed_label(speed),
        )

    def get_status(self) -> dict:
        """Return current playback status.

        Returns:
            dict: Status with keys:
                - state: "idle" | "playing" | "paused"
                - speed: Current speed multiplier
                - speed_label: Human-readable speed name
                - progress: Fraction complete (0.0 to 1.0)
                - records_inserted: Count of records inserted
                - total_records: Total records in fixture
                - simulated_time: Formatted time (T+Xh)
                - simulated_hours: Decimal hours elapsed
        """
        if self.fixture is None:
            return {
                "state": self.state,
                "speed": self.speed,
                "speed_label": self._get_speed_label(),
                "progress": 0.0,
                "records_inserted": 0,
                "total_records": 0,
                "simulated_time": "T+0h",
                "simulated_hours": 0.0,
            }

        total_records = len(self.fixture["records"])
        progress = self.current_index / total_records if total_records > 0 else 0.0

        return {
            "state": self.state,
            "speed": self.speed,
            "speed_label": self._get_speed_label(),
            "progress": round(progress, 3),
            "records_inserted": self.records_inserted,
            "total_records": total_records,
            "simulated_time": self._format_simulated_time(),
            "simulated_hours": round(self._calculate_simulated_hours(), 1),
        }

    async def _playback_loop(self) -> None:
        """Core loop that iterates through fixture records with timing control.

        For each record:
        1. Calculate delay from previous record (adjusted by speed multiplier)
        2. Sleep with interruptible chunks for responsive control
        3. Insert record into Supabase
        4. Update progress tracking

        Stops when:
        - All records processed (sets state to "idle")
        - State changes to "paused" (preserves position for resume)
        """
        try:
            records = self.fixture["records"]
            previous_offset = records[self.current_index]["_demo_offset_seconds"] if self.current_index > 0 else 0.0

            while self.current_index < len(records):
                # Check if paused or stopped
                if self.state != "playing":
                    logger.info("playback_loop_stopped", reason=self.state)
                    break

                record = records[self.current_index]
                current_offset = record["_demo_offset_seconds"]

                # Calculate delay from previous record
                delay_seconds = (current_offset - previous_offset) / self.speed

                # Wait with interruptible sleep
                if delay_seconds > 0:
                    await self._interruptible_sleep(delay_seconds)

                # Check again after sleep (might have paused during delay)
                if self.state != "playing":
                    logger.info("playback_loop_stopped", reason=self.state)
                    break

                # Insert record
                await self._insert_record(record)

                # Update tracking
                self.current_index += 1
                self.records_inserted += 1
                self.simulated_seconds_elapsed = current_offset
                previous_offset = current_offset

            # If we completed all records, set state to idle
            if self.current_index >= len(records) and self.state == "playing":
                self.state = "idle"
                logger.info(
                    "playback_complete",
                    total_records=len(records),
                    final_simulated_time=self._format_simulated_time(),
                )

        except Exception as e:
            logger.error("playback_loop_error", error=str(e), exc_info=True)
            self.state = "idle"
            raise

    async def _interruptible_sleep(self, seconds: float) -> None:
        """Sleep in small increments so pause/reset can interrupt quickly.

        Args:
            seconds: Total seconds to sleep

        Sleeps in 0.1s chunks, checking state after each chunk.
        Breaks early if state changes from "playing".
        """
        elapsed = 0.0
        chunk_size = 0.1

        while elapsed < seconds:
            if self.state != "playing":
                break

            sleep_duration = min(chunk_size, seconds - elapsed)
            await asyncio.sleep(sleep_duration)
            elapsed += sleep_duration

    async def _insert_record(self, record: dict) -> None:
        """Insert single record into correct Supabase table.

        Args:
            record: Record with keys:
                - _table: Target table name
                - _demo_action: "insert" or "update"
                - data: Record fields to insert

        Handles:
        - articles: upsert on "url" conflict
        - social_posts, vessel_positions: plain insert
        - narrative_events, movement_events: plain insert
        - alerts: INSERT stores id, UPDATE uses stored id
        - briefs: plain insert
        """
        table = record["_table"]
        action = record["_demo_action"]
        data = record["data"]

        try:
            client = await get_supabase()

            # Route to correct table with appropriate insert/upsert logic
            if table == "articles":
                # Upsert on URL conflict
                result = await client.table(table).upsert(data).execute()
                logger.info("record_inserted", table=table, action="upsert", url=data.get("url"))

            elif table == "alerts":
                if action == "insert":
                    # First alert - insert and store ID
                    result = await client.table(table).insert(data).execute()
                    if result.data:
                        self.alert_id = result.data[0]["id"]
                    logger.info("alert_inserted", alert_id=self.alert_id, threat_level=data.get("threat_level"))
                elif action == "update":
                    # Subsequent alert - update by stored ID
                    if self.alert_id is None:
                        logger.error("alert_update_failed", reason="no_alert_id_stored")
                        return
                    result = await client.table(table).update(data).eq("id", self.alert_id).execute()
                    logger.info("alert_updated", alert_id=self.alert_id, threat_level=data.get("threat_level"))

            else:
                # Plain insert for all other tables
                result = await client.table(table).insert(data).execute()
                logger.info("record_inserted", table=table, action="insert")

        except Exception as e:
            logger.error(
                "record_insert_failed",
                table=table,
                action=action,
                error=str(e),
                exc_info=True,
            )
            # Don't raise - continue with next record

    async def _clear_tables(self) -> None:
        """Delete all rows from all 7 Supabase tables.

        Deletion order matters:
        1. briefs (references alerts)
        2. alerts (references events)
        3. movement_events, narrative_events
        4. vessel_positions, social_posts, articles (raw data)
        """
        client = await get_supabase()

        # Delete in dependency order
        tables_to_clear = [
            "briefs",
            "alerts",
            "movement_events",
            "narrative_events",
            "vessel_positions",
            "social_posts",
            "articles",
        ]

        for table in tables_to_clear:
            try:
                # Delete all rows (Supabase requires a filter, use neq on id with impossible value)
                await client.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                logger.info("table_cleared", table=table)
            except Exception as e:
                logger.error("table_clear_failed", table=table, error=str(e))

    def _get_speed_label(self, speed: float | None = None) -> str:
        """Get human-readable speed label.

        Args:
            speed: Speed value to label (defaults to self.speed)

        Returns:
            str: "slow" | "normal" | "fast"
        """
        if speed is None:
            speed = self.speed

        if speed <= 0.5:
            return "slow"
        elif speed <= 1.5:
            return "normal"
        else:
            return "fast"

    def _format_simulated_time(self) -> str:
        """Format simulated time as T+Xh.

        Maps 300 seconds real time -> 72 hours simulated time.

        Returns:
            str: Formatted time like "T+32h"
        """
        hours = self._calculate_simulated_hours()
        return f"T+{hours:.0f}h"

    def _calculate_simulated_hours(self) -> float:
        """Calculate simulated hours elapsed.

        Maps: 300 seconds real time -> 72 hours simulated time
        Formula: hours = (simulated_seconds_elapsed / 300) * 72

        Returns:
            float: Decimal hours elapsed
        """
        if self.simulated_seconds_elapsed == 0.0:
            return 0.0

        return (self.simulated_seconds_elapsed / 300.0) * 72.0


# Module-level singleton
demo_engine = DemoEngine()
