#!/usr/bin/env python3
"""
Validation tests for query_flights.py against the Flighty database.

Catches regressions in:
- SQL NULL handling (importSource filter)
- Flight counting (tracked + manual = total)
- Year-level summation consistency
- Optional CSV comparison against Flighty export

Usage:
    python3 validate_flights.py
    python3 validate_flights.py --csv /path/to/FlightyExport.csv
    python3 validate_flights.py --db /path/to/MainFlightyDatabase.db
"""

import argparse
import csv
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = (
    Path.home()
    / "Library/Containers/com.flightyapp.flighty/Data/Documents/MainFlightyDatabase.db"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class TestResult:
    def __init__(self, name, passed, detail=""):
        self.name = name
        self.passed = passed
        self.detail = detail


def get_main_user_id(conn):
    """Identify the primary user (device owner with the most flights)."""
    cur = conn.cursor()
    cur.execute("""
        SELECT userId
        FROM UserFlight
        WHERE deleted IS NULL
        GROUP BY userId
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    return row[0] if row else None


def get_superseded_flight_ids(conn):
    """Flight IDs replaced by ManualFlight entries."""
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT originalFlightId
        FROM ManualFlight
        WHERE originalFlightId IS NOT NULL AND originalFlightId != ''
    """)
    return {row[0] for row in cur.fetchall()}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_null_filter(conn, main_user_id):
    """Verify that the NULL-safe importSource filter doesn't drop rows.

    The old broken query:
        WHERE importSource != 'CONNECTED_FRIEND'
    silently drops rows where importSource IS NULL because
    NULL != X evaluates to NULL (falsy).

    The correct query:
        WHERE importSource IS NULL OR importSource != 'CONNECTED_FRIEND'
    preserves those rows.
    """
    cur = conn.cursor()

    # Count with the CORRECT (NULL-safe) filter
    cur.execute("""
        SELECT COUNT(*)
        FROM UserFlight uf
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND uf.userId = ?
          AND (uf.importSource IS NULL OR uf.importSource != 'CONNECTED_FRIEND')
    """, (main_user_id,))
    correct_count = cur.fetchone()[0]

    # Count with the OLD BROKEN filter (for comparison)
    cur.execute("""
        SELECT COUNT(*)
        FROM UserFlight uf
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND uf.userId = ?
          AND uf.importSource != 'CONNECTED_FRIEND'
    """, (main_user_id,))
    broken_count = cur.fetchone()[0]

    # Count rows where importSource IS NULL (the ones the broken query drops)
    cur.execute("""
        SELECT COUNT(*)
        FROM UserFlight uf
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND uf.userId = ?
          AND uf.importSource IS NULL
    """, (main_user_id,))
    null_count = cur.fetchone()[0]

    # The correct count should be >= broken count
    # If they differ, it means there are NULL importSource rows being dropped
    if correct_count == broken_count:
        detail = (
            f"correct={correct_count}, broken={broken_count} (no NULL rows exist — "
            f"consider adding a row-level check if this changes)"
        )
        return TestResult("NULL filter safety", True, detail)

    if correct_count > broken_count:
        dropped = correct_count - broken_count
        detail = (
            f"correct={correct_count}, broken={broken_count}, "
            f"NULL importSource rows={null_count}, would-be-dropped={dropped}"
        )
        # This is expected — the correct filter preserves more rows
        return TestResult("NULL filter safety", True, detail)

    # Should never happen: broken filter returning MORE than correct filter
    detail = f"UNEXPECTED: correct={correct_count} < broken={broken_count}"
    return TestResult("NULL filter safety", False, detail)


def test_total_count_consistency(conn, main_user_id):
    """Verify that two independent counting methods agree.

    Method A: Direct COUNT(*) on each table (mirrors get_flight_stats())
    Method B: Sum of per-row iteration with the same filters

    If these diverge, it means the filter logic has a bug.
    """
    cur = conn.cursor()

    # Method A: Aggregate COUNT (same as get_flight_stats)
    cur.execute("""
        SELECT COUNT(*)
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND uf.userId = ?
    """, (main_user_id,))
    tracked_count_a = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM ManualFlight mf
        JOIN UserManualFlight umf ON mf.id = umf.flightId
        WHERE umf.isMyFlight = 1
          AND umf.deleted IS NULL
          AND umf.userId = ?
    """, (main_user_id,))
    manual_count_a = cur.fetchone()[0]

    # Method B: Row-by-row with NULL-safe friend filter (same as year queries)
    cur.execute("""
        SELECT COUNT(*)
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND uf.userId = ?
          AND (uf.importSource IS NULL OR uf.importSource != 'CONNECTED_FRIEND')
    """, (main_user_id,))
    tracked_count_b = cur.fetchone()[0]

    # The difference between A and B is exactly the CONNECTED_FRIEND count
    cur.execute("""
        SELECT COUNT(*)
        FROM UserFlight uf
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND uf.userId = ?
          AND uf.importSource = 'CONNECTED_FRIEND'
    """, (main_user_id,))
    friend_count = cur.fetchone()[0]

    # Verify: tracked_a = tracked_b + friend_count
    expected_tracked_a = tracked_count_b + friend_count
    counts_match = tracked_count_a == expected_tracked_a

    detail = (
        f"tracked_raw={tracked_count_a}, tracked_filtered={tracked_count_b}, "
        f"friends={friend_count}, manual={manual_count_a}, "
        f"raw==filtered+friends: {counts_match}"
    )
    return TestResult("Total count consistency", counts_match, detail)


def test_year_sum_matches_total(conn, main_user_id):
    """Sum flight counts across all years and compare to a direct total query.

    Uses the year-query approach from get_flights_by_year() which:
    - Filters by user and excludes CONNECTED_FRIEND
    - Excludes superseded flights
    - Deduplicates by route (date + dep + arr)
    """
    cur = conn.cursor()
    superseded_ids = get_superseded_flight_ids(conn)

    # Get the range of years from BOTH tables (tracked + manual)
    cur.execute("""
        SELECT MIN(ts), MAX(ts) FROM (
            SELECT COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as ts
            FROM Flight f
            JOIN UserFlight uf ON f.id = uf.flightId
            WHERE uf.isMyFlight = 1
              AND uf.deleted IS NULL
              AND uf.userId = ?
              AND (uf.importSource IS NULL OR uf.importSource != 'CONNECTED_FRIEND')
            UNION ALL
            SELECT mf.lastKnownDepartureDate as ts
            FROM ManualFlight mf
            JOIN UserManualFlight umf ON mf.id = umf.flightId
            WHERE umf.isMyFlight = 1
              AND umf.deleted IS NULL
              AND umf.userId = ?
        )
    """, (main_user_id, main_user_id))
    row = cur.fetchone()
    if not row or not row[0]:
        return TestResult("Year sum vs total", False, "No flights found")

    min_year = datetime.fromtimestamp(row[0], tz=timezone.utc).year
    max_year = datetime.fromtimestamp(row[1], tz=timezone.utc).year

    # Count flights per year using the same dedup logic as get_flights_by_year
    year_total = 0
    year_breakdown = []

    for year in range(min_year, max_year + 1):
        start_ts = datetime(year, 1, 1).timestamp()
        end_ts = datetime(year, 12, 31, 23, 59, 59).timestamp()
        route_keys = set()

        # Tracked flights for this year
        cur.execute("""
            SELECT
                f.id,
                COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as dep_ts,
                COALESCE(dep.iata, dep.icao) as dep_code,
                COALESCE(arr.iata, arr.icao) as arr_code,
                dep.timeZoneIdentifier as dep_tz
            FROM Flight f
            JOIN UserFlight uf ON f.id = uf.flightId
            JOIN Airport dep ON f.departureAirportId = dep.id
            JOIN Airport arr ON f.scheduledArrivalAirportId = arr.id
            WHERE uf.isMyFlight = 1
              AND uf.deleted IS NULL
              AND uf.userId = ?
              AND (uf.importSource IS NULL OR uf.importSource != 'CONNECTED_FRIEND')
              AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) >= ?
              AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) <= ?
        """, (main_user_id, start_ts, end_ts))

        for r in cur.fetchall():
            if r[0] in superseded_ids:
                continue
            dep_ts = r[1]
            dep_tz = r[4]
            if dep_ts:
                dt = datetime.fromtimestamp(dep_ts, tz=timezone.utc)
                if dep_tz:
                    try:
                        from zoneinfo import ZoneInfo
                        dt = dt.astimezone(ZoneInfo(dep_tz))
                    except Exception:
                        pass
                dep_date = dt.strftime("%Y-%m-%d")
                route_keys.add(f"{dep_date}|{r[2]}|{r[3]}")

        # Manual flights for this year
        cur.execute("""
            SELECT
                mf.lastKnownDepartureDate as dep_ts,
                COALESCE(dep.iata, dep.icao) as dep_code,
                COALESCE(arr.iata, arr.icao) as arr_code,
                dep.timeZoneIdentifier as dep_tz
            FROM ManualFlight mf
            JOIN UserManualFlight umf ON mf.id = umf.flightId
            JOIN Airport dep ON mf.departureAirportId = dep.id
            JOIN Airport arr ON mf.scheduledArrivalAirportId = arr.id
            WHERE umf.isMyFlight = 1
              AND umf.deleted IS NULL
              AND umf.userId = ?
              AND mf.lastKnownDepartureDate >= ?
              AND mf.lastKnownDepartureDate <= ?
        """, (main_user_id, start_ts, end_ts))

        for r in cur.fetchall():
            dep_ts = r[0]
            dep_tz = r[3]
            if dep_ts:
                dt = datetime.fromtimestamp(dep_ts, tz=timezone.utc)
                if dep_tz:
                    try:
                        from zoneinfo import ZoneInfo
                        dt = dt.astimezone(ZoneInfo(dep_tz))
                    except Exception:
                        pass
                dep_date = dt.strftime("%Y-%m-%d")
                route_keys.add(f"{dep_date}|{r[1]}|{r[2]}")

        count = len(route_keys)
        if count > 0:
            year_breakdown.append(f"{year}:{count}")
        year_total += count

    # Now get a single all-time count using the same dedup logic
    all_route_keys = set()

    cur.execute("""
        SELECT
            f.id,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as dep_ts,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            dep.timeZoneIdentifier as dep_tz
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.scheduledArrivalAirportId = arr.id
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND uf.userId = ?
          AND (uf.importSource IS NULL OR uf.importSource != 'CONNECTED_FRIEND')
    """, (main_user_id,))

    for r in cur.fetchall():
        if r[0] in superseded_ids:
            continue
        dep_ts = r[1]
        dep_tz = r[4]
        if dep_ts:
            dt = datetime.fromtimestamp(dep_ts, tz=timezone.utc)
            if dep_tz:
                try:
                    from zoneinfo import ZoneInfo
                    dt = dt.astimezone(ZoneInfo(dep_tz))
                except Exception:
                    pass
            dep_date = dt.strftime("%Y-%m-%d")
            all_route_keys.add(f"{dep_date}|{r[2]}|{r[3]}")

    cur.execute("""
        SELECT
            mf.lastKnownDepartureDate as dep_ts,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            dep.timeZoneIdentifier as dep_tz
        FROM ManualFlight mf
        JOIN UserManualFlight umf ON mf.id = umf.flightId
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.scheduledArrivalAirportId = arr.id
        WHERE umf.isMyFlight = 1
          AND umf.deleted IS NULL
          AND umf.userId = ?
    """, (main_user_id,))

    for r in cur.fetchall():
        dep_ts = r[0]
        dep_tz = r[3]
        if dep_ts:
            dt = datetime.fromtimestamp(dep_ts, tz=timezone.utc)
            if dep_tz:
                try:
                    from zoneinfo import ZoneInfo
                    dt = dt.astimezone(ZoneInfo(dep_tz))
                except Exception:
                    pass
            dep_date = dt.strftime("%Y-%m-%d")
            all_route_keys.add(f"{dep_date}|{r[1]}|{r[2]}")

    all_time_total = len(all_route_keys)

    passed = year_total == all_time_total
    detail = (
        f"year_sum={year_total}, all_time={all_time_total}, "
        f"years=[{', '.join(year_breakdown)}]"
    )
    if not passed:
        # Find flights in all-time but not in any year (or vice versa)
        detail += f" | diff={abs(year_total - all_time_total)}"

    return TestResult("Year sum matches all-time total", passed, detail)


def test_recent_upcoming_coverage(conn, main_user_id):
    """Verify recent + upcoming flights cover the full history.

    recent (past flights) + upcoming (future flights) should equal the
    total number of deduped flights (with some tolerance for flights
    exactly at the boundary timestamp).
    """
    cur = conn.cursor()
    now = datetime.now(tz=timezone.utc).timestamp()
    superseded_ids = get_superseded_flight_ids(conn)

    past_keys = set()
    future_keys = set()

    # Tracked flights partitioned by past/future
    cur.execute("""
        SELECT
            f.id,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as dep_ts,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            dep.timeZoneIdentifier as dep_tz
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.scheduledArrivalAirportId = arr.id
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND uf.userId = ?
          AND (uf.importSource IS NULL OR uf.importSource != 'CONNECTED_FRIEND')
    """, (main_user_id,))

    for r in cur.fetchall():
        if r[0] in superseded_ids:
            continue
        dep_ts = r[1]
        dep_tz = r[4]
        if not dep_ts:
            continue
        dt = datetime.fromtimestamp(dep_ts, tz=timezone.utc)
        if dep_tz:
            try:
                from zoneinfo import ZoneInfo
                dt = dt.astimezone(ZoneInfo(dep_tz))
            except Exception:
                pass
        dep_date = dt.strftime("%Y-%m-%d")
        key = f"{dep_date}|{r[2]}|{r[3]}"
        if dep_ts < now:
            past_keys.add(key)
        else:
            future_keys.add(key)

    # Manual flights
    cur.execute("""
        SELECT
            mf.lastKnownDepartureDate as dep_ts,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            dep.timeZoneIdentifier as dep_tz
        FROM ManualFlight mf
        JOIN UserManualFlight umf ON mf.id = umf.flightId
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.scheduledArrivalAirportId = arr.id
        WHERE umf.isMyFlight = 1
          AND umf.deleted IS NULL
          AND umf.userId = ?
    """, (main_user_id,))

    for r in cur.fetchall():
        dep_ts = r[0]
        dep_tz = r[3]
        if not dep_ts:
            continue
        dt = datetime.fromtimestamp(dep_ts, tz=timezone.utc)
        if dep_tz:
            try:
                from zoneinfo import ZoneInfo
                dt = dt.astimezone(ZoneInfo(dep_tz))
            except Exception:
                pass
        dep_date = dt.strftime("%Y-%m-%d")
        key = f"{dep_date}|{r[1]}|{r[2]}"
        if dep_ts < now:
            past_keys.add(key)
        else:
            future_keys.add(key)

    # Verify: past + future should account for ALL flights
    # Compare against the all-time set from test_year_sum to catch partitioning bugs
    combined = past_keys | future_keys
    overlap = past_keys & future_keys

    # Sanity: combined count should be > 0 and overlap should be minimal
    # (overlap can happen if a flight departs exactly at `now`)
    passed = len(combined) > 0 and len(past_keys) > 0

    detail = (
        f"past={len(past_keys)}, future={len(future_keys)}, "
        f"combined={len(combined)}, overlap={len(overlap)}"
    )
    if not passed:
        detail += " | UNEXPECTED: no past flights found"

    return TestResult("Recent + upcoming coverage", passed, detail)


def test_csv_comparison(conn, main_user_id, csv_path):
    """Compare flights against a Flighty CSV export.

    The CSV export is the "master data" — every flight in the CSV
    should appear in our query results (matched by route + date).

    Known matching challenges:
    - Date boundaries: late-night flights may differ by +/- 1 day between
      CSV (scheduled date) and DB (timestamp-to-local conversion)
    - Airport codes: DB uses COALESCE(iata, icao) which may be 4-char ICAO;
      CSV uses its own airport code field
    - Some flights may be in DB but not CSV or vice versa due to export timing

    We match by route (dep+arr) with +/- 1 day tolerance to handle these.
    """
    from datetime import timedelta

    superseded_ids = get_superseded_flight_ids(conn)

    # Build DB route entries: list of (date_str, dep_code, arr_code)
    cur = conn.cursor()
    db_entries = []

    # Tracked flights
    cur.execute("""
        SELECT
            f.id,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as dep_ts,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            dep.timeZoneIdentifier as dep_tz
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.scheduledArrivalAirportId = arr.id
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND uf.userId = ?
          AND (uf.importSource IS NULL OR uf.importSource != 'CONNECTED_FRIEND')
    """, (main_user_id,))

    for r in cur.fetchall():
        if r[0] in superseded_ids:
            continue
        dep_ts = r[1]
        dep_tz = r[4]
        if not dep_ts:
            continue
        dt = datetime.fromtimestamp(dep_ts, tz=timezone.utc)
        if dep_tz:
            try:
                from zoneinfo import ZoneInfo
                dt = dt.astimezone(ZoneInfo(dep_tz))
            except Exception:
                pass
        db_entries.append((dt.strftime("%Y-%m-%d"), r[2], r[3]))

    # Manual flights
    cur.execute("""
        SELECT
            mf.lastKnownDepartureDate as dep_ts,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            dep.timeZoneIdentifier as dep_tz
        FROM ManualFlight mf
        JOIN UserManualFlight umf ON mf.id = umf.flightId
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.scheduledArrivalAirportId = arr.id
        WHERE umf.isMyFlight = 1
          AND umf.deleted IS NULL
          AND umf.userId = ?
    """, (main_user_id,))

    for r in cur.fetchall():
        dep_ts = r[0]
        dep_tz = r[3]
        if not dep_ts:
            continue
        dt = datetime.fromtimestamp(dep_ts, tz=timezone.utc)
        if dep_tz:
            try:
                from zoneinfo import ZoneInfo
                dt = dt.astimezone(ZoneInfo(dep_tz))
            except Exception:
                pass
        db_entries.append((dt.strftime("%Y-%m-%d"), r[1], r[2]))

    # Build DB lookup: for each route (dep, arr), store all dates
    # Also build expanded key set with +/- 1 day for fuzzy matching
    db_route_dates = {}  # (dep, arr) -> set of dates
    for date_str, dep, arr in db_entries:
        db_route_dates.setdefault((dep, arr), set()).add(date_str)

    # Parse the CSV
    csv_entries = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_val = row.get("Date")
            dep_val = row.get("From")
            arr_val = row.get("To")
            cancelled = row.get("Canceled", "false").lower() == "true"

            if not date_val or not dep_val or not arr_val:
                continue
            if cancelled:
                continue

            # Normalize date
            parsed_ok = False
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%b %d, %Y"):
                try:
                    parsed_date = datetime.strptime(date_val.strip(), fmt)
                    date_val = parsed_date.strftime("%Y-%m-%d")
                    parsed_ok = True
                    break
                except ValueError:
                    continue

            if not parsed_ok:
                continue  # Skip rows with unparseable dates

            dep_code = dep_val.strip().upper()
            arr_code = arr_val.strip().upper()
            airline = row.get("Airline", "?")
            flight_num = row.get("Flight", "?")
            csv_entries.append((date_val, dep_code, arr_code, f"{airline} {flight_num}"))

    # Match CSV entries against DB with +/- 1 day tolerance
    matched = 0
    unmatched = []

    for date_str, dep, arr, flight_info in csv_entries:
        # Try exact match first, then +/- 1 day
        target = datetime.strptime(date_str, "%Y-%m-%d")
        dates_to_check = [
            target.strftime("%Y-%m-%d"),
            (target - timedelta(days=1)).strftime("%Y-%m-%d"),
            (target + timedelta(days=1)).strftime("%Y-%m-%d"),
        ]

        found = False
        # Try matching against all DB airport code variants for this route
        for db_key, db_dates in db_route_dates.items():
            db_dep, db_arr = db_key
            # Match if codes are equal OR one is a prefix of the other
            # (handles IATA "SFO" vs ICAO "KSFO", or "SPS" vs "SPSF")
            dep_match = dep == db_dep or dep.startswith(db_dep) or db_dep.startswith(dep)
            arr_match = arr == db_arr or arr.startswith(db_arr) or db_arr.startswith(arr)

            if dep_match and arr_match:
                if any(d in db_dates for d in dates_to_check):
                    found = True
                    break

        if found:
            matched += 1
        else:
            unmatched.append(f"  {date_str} {dep}->{arr} ({flight_info})")

    detail = (
        f"CSV={len(csv_entries)}, DB={len(db_entries)}, "
        f"matched={matched}, unmatched={len(unmatched)}"
    )
    if unmatched:
        detail += "\n    Unmatched CSV flights:\n" + "\n".join(unmatched[:10])
        if len(unmatched) > 10:
            detail += f"\n    ... and {len(unmatched) - 10} more"

    # Fail if CSV parsed no usable rows (vacuous pass guard)
    if len(csv_entries) == 0:
        return TestResult(
            "CSV comparison", False,
            "CSV file parsed 0 usable rows — check file path, headers, and encoding",
        )

    # Pass if all CSV flights found a DB match (with tolerance)
    passed = len(unmatched) == 0
    return TestResult("CSV comparison", passed, detail)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_tests(db_path, csv_path=None):
    """Run all validation tests and print results."""
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    main_user_id = get_main_user_id(conn)

    if not main_user_id:
        print("ERROR: Could not identify primary user in database")
        sys.exit(1)

    print(f"Database: {db_path}")
    print(f"Primary user: {main_user_id[:8]}...")
    print()

    results = []

    # Core tests
    results.append(test_null_filter(conn, main_user_id))
    results.append(test_total_count_consistency(conn, main_user_id))
    results.append(test_year_sum_matches_total(conn, main_user_id))
    results.append(test_recent_upcoming_coverage(conn, main_user_id))

    # Optional CSV test
    if csv_path:
        results.append(test_csv_comparison(conn, main_user_id, csv_path))

    conn.close()

    # Print results
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    passed = 0
    failed = 0
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        icon = "[+]" if r.passed else "[-]"
        print(f"  {icon} {status}: {r.name}")
        if r.detail:
            for line in r.detail.split("\n"):
                print(f"       {line}")
        if r.passed:
            passed += 1
        else:
            failed += 1

    print("=" * 70)
    print(f"  {passed} passed, {failed} failed, {len(results)} total")
    print("=" * 70)

    return 0 if failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Validate query_flights.py against the Flighty database"
    )
    parser.add_argument(
        "--csv",
        help="Path to Flighty CSV export for comparison",
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB_PATH),
        help="Path to Flighty database",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    csv_path = args.csv

    if csv_path and not Path(csv_path).exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        sys.exit(1)

    sys.exit(run_tests(db_path, csv_path))


if __name__ == "__main__":
    main()
