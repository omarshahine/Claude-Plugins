#!/usr/bin/env python3
"""
Query Flighty database for detailed flight information.
Outputs structured JSON for easy parsing by Claude.

Flighty stores flights in two tables:
- Flight: Tracked flights (via ADS-B, airline APIs) linked via UserFlight
- ManualFlight: Manually entered flights linked via UserManualFlight

This script queries both tables to get the complete flight history.
"""

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# Flighty database location (macOS)
DEFAULT_DB_PATH = Path.home() / "Library/Containers/com.flightyapp.flighty/Data/Documents/MainFlightyDatabase.db"


def get_db_path():
    """Get database path, checking if it exists."""
    db_path = DEFAULT_DB_PATH
    if not db_path.exists():
        return None, f"Database not found at {db_path}"
    return db_path, None


def convert_timestamp(ts, tz_name=None):
    """Convert Unix timestamp to ISO format in the given timezone."""
    if ts is None:
        return None
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    if tz_name:
        try:
            dt = dt.astimezone(ZoneInfo(tz_name))
        except (KeyError, Exception):
            pass
    return dt.isoformat()


def convert_date(ts, tz_name=None):
    """Convert Unix timestamp to date string in the given timezone."""
    if ts is None:
        return None
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    if tz_name:
        try:
            dt = dt.astimezone(ZoneInfo(tz_name))
        except (KeyError, Exception):
            pass
    return dt.strftime("%Y-%m-%d")


def format_datetime(ts, tz_name=None):
    """Format timestamp for display in the given timezone."""
    if ts is None:
        return None
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    if tz_name:
        try:
            dt = dt.astimezone(ZoneInfo(tz_name))
        except (KeyError, Exception):
            pass
    return dt.strftime("%b %d, %Y %I:%M %p")


def calculate_duration(departure, arrival):
    """Calculate flight duration in hours and minutes."""
    if departure is None or arrival is None:
        return None
    duration_seconds = arrival - departure
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    return f"{hours}h {minutes}m"


def days_until(ts):
    """Calculate days until a timestamp."""
    if ts is None:
        return None
    target = datetime.fromtimestamp(ts, tz=timezone.utc)
    delta = target - datetime.now(tz=timezone.utc)
    return delta.days


def get_main_user_id(conn):
    """Identify the main user (device owner with the most flights)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT userId
        FROM UserFlight
        WHERE deleted IS NULL
        GROUP BY userId
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    return row[0] if row else None


def get_superseded_flight_ids(conn):
    """Get Flight IDs that have been superseded by ManualFlight entries.

    When a ManualFlight has originalFlightId set, it means the ManualFlight
    is a corrected/richer version of the original Flight table entry.
    The Flight table entry should be excluded to avoid duplicates.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT originalFlightId
        FROM ManualFlight
        WHERE originalFlightId IS NOT NULL AND originalFlightId != ''
    """)
    return {row[0] for row in cursor.fetchall()}


def query_tracked_upcoming(conn, now, main_user_id, include_friends, limit):
    """Query tracked flights (Flight table) for upcoming flights."""
    cursor = conn.cursor()
    superseded_ids = get_superseded_flight_ids(conn)

    if include_friends:
        where_clause = "uf.isMyFlight = 1 AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) > ?"
        params = [now]
    else:
        where_clause = """
            uf.isMyFlight = 1
            AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) > ?
            AND uf.userId = ?
            AND uf.importSource != 'CONNECTED_FRIEND'
        """
        params = [now, main_user_id]

    cursor.execute(f"""
        SELECT
            a.iata as airline_code,
            a.name as airline_name,
            f.number as flight_number,
            COALESCE(dep.iata, dep.icao) as dep_code,
            dep.name as dep_airport,
            dep.city as dep_city,
            COALESCE(arr.iata, arr.icao) as arr_code,
            arr.name as arr_airport,
            arr.city as arr_city,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as departure,
            COALESCE(f.lastKnownArrivalDate, f.arrivalScheduleGateOriginal) as arrival,
            t.pnr as confirmation,
            t.seatNumber as seat,
            t.cabinClass as cabin_class,
            COALESCE(at.name, f.equipmentModelName) as aircraft,
            f.departureTerminal as dep_terminal,
            f.departureGate as dep_gate,
            f.arrivalTerminal as arr_terminal,
            f.arrivalGate as arr_gate,
            f.distance as distance_km,
            uf.importSource as import_source,
            f.equipmentTailNumber as tail_number,
            'tracked' as source,
            f.id as flight_id,
            dep.timeZoneIdentifier as dep_tz
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airline a ON f.airlineId = a.id
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.scheduledArrivalAirportId = arr.id
        LEFT JOIN AircraftType at ON f.equipmentModelId = at.id
        LEFT JOIN Ticket t ON f.id = t.flightId AND uf.userId = t.userId
        WHERE {where_clause}
        ORDER BY departure
        LIMIT ?
    """, params + [limit * 2])  # Fetch extra to allow for merging

    # Filter out flights superseded by ManualFlight entries
    rows = cursor.fetchall()
    return [row for row in rows if row[23] not in superseded_ids]


def query_manual_upcoming(conn, now, main_user_id, limit):
    """Query manual flights (ManualFlight table) for upcoming flights."""
    cursor = conn.cursor()

    user_filter = ""
    params = [now]
    if main_user_id:
        user_filter = "AND umf.userId = ?"
        params.append(main_user_id)

    cursor.execute(f"""
        SELECT
            a.iata as airline_code,
            a.name as airline_name,
            mf.number as flight_number,
            COALESCE(dep.iata, dep.icao) as dep_code,
            dep.name as dep_airport,
            dep.city as dep_city,
            COALESCE(arr.iata, arr.icao) as arr_code,
            arr.name as arr_airport,
            arr.city as arr_city,
            mf.lastKnownDepartureDate as departure,
            mf.lastKnownArrivalDate as arrival,
            NULL as confirmation,
            NULL as seat,
            NULL as cabin_class,
            COALESCE(at.name, mf.equipmentModelName) as aircraft,
            mf.departureTerminal as dep_terminal,
            mf.departureGate as dep_gate,
            mf.arrivalTerminal as arr_terminal,
            mf.arrivalGate as arr_gate,
            mf.distance as distance_km,
            'MANUAL' as import_source,
            mf.equipmentTailNumber as tail_number,
            'manual' as source,
            NULL as flight_id,
            dep.timeZoneIdentifier as dep_tz
        FROM ManualFlight mf
        JOIN UserManualFlight umf ON mf.id = umf.flightId
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.scheduledArrivalAirportId = arr.id
        LEFT JOIN Airline a ON mf.airlineId = a.id
        LEFT JOIN AircraftType at ON mf.equipmentModelId = at.id
        WHERE umf.isMyFlight = 1
          AND umf.deleted IS NULL
          AND mf.lastKnownDepartureDate > ?
          {user_filter}
        ORDER BY mf.lastKnownDepartureDate
        LIMIT ?
    """, params + [limit * 2])

    return cursor.fetchall()


def process_flight_row(row):
    """Process a flight row into a dictionary.

    Row layout (indices 0-24):
      0: airline_code, 1: airline_name, 2: flight_number,
      3: dep_code, 4: dep_airport, 5: dep_city,
      6: arr_code, 7: arr_airport, 8: arr_city,
      9: departure_ts, 10: arrival_ts,
      11: confirmation, 12: seat, 13: cabin_class, 14: aircraft,
      15: dep_terminal, 16: dep_gate, 17: arr_terminal, 18: arr_gate,
      19: distance_km, 20: import_source, 21: tail_number, 22: source,
      23: flight_id, 24: dep_tz
    """
    cabin_class = row[13]
    if cabin_class:
        cabin_display = cabin_class.replace("premiumEconomy", "Premium Economy").replace("privateJet", "Private Jet").title()
    else:
        cabin_display = None

    departure_ts = row[9]
    arrival_ts = row[10]
    dep_tz = row[24] if len(row) > 24 else None

    source = row[22]
    # Manual flight numbers already include the airline/operator prefix (e.g., "EJA 431")
    # Tracked flight numbers are just the numeric part (e.g., "123") and need the IATA code prepended
    if source == 'manual':
        flight_display = row[2]
    else:
        flight_display = f"{row[0]} {row[2]}" if row[0] and row[2] else row[2]

    return {
        "flight": flight_display,
        "airline": row[1],
        "flight_number": row[2],
        "route": f"{row[3]} → {row[6]}",
        "departure": {
            "airport_code": row[3],
            "airport_name": row[4],
            "city": row[5],
            "datetime": convert_timestamp(departure_ts, dep_tz),
            "display": format_datetime(departure_ts, dep_tz),
            "terminal": row[15],
            "gate": row[16]
        },
        "arrival": {
            "airport_code": row[6],
            "airport_name": row[7],
            "city": row[8],
            "datetime": convert_timestamp(arrival_ts),
            "display": format_datetime(arrival_ts),
            "terminal": row[17],
            "gate": row[18]
        },
        "confirmation": row[11],
        "seat": row[12],
        "cabin_class": cabin_display,
        "aircraft": row[14],
        "duration": calculate_duration(departure_ts, arrival_ts),
        "distance_km": row[19],
        "distance_miles": int(row[19] * 0.621371) if row[19] else None,
        "days_until": days_until(departure_ts),
        "import_source": row[20],
        "tail_number": row[21],
        "source": row[22],
        "_departure_ts": departure_ts,  # For sorting
        "_dep_tz": dep_tz  # For timezone-aware date display
    }


def list_upcoming_flights(conn, limit=20, include_friends=False):
    """List all upcoming flights with full details from both tables."""
    now = datetime.now().timestamp()
    main_user_id = get_main_user_id(conn)

    # Get flights from both tables
    tracked_rows = query_tracked_upcoming(conn, now, main_user_id, include_friends, limit)
    manual_rows = query_manual_upcoming(conn, now, main_user_id, limit)

    # Process and combine
    flights = []
    seen_keys = set()

    for row in tracked_rows:
        flight = process_flight_row(row)
        # Dedup key: date (in departure timezone) + route + flight number
        dep_date = convert_date(flight["_departure_ts"], flight.get("_dep_tz"))
        key = f"{dep_date}|{flight['departure']['airport_code']}|{flight['arrival']['airport_code']}|{flight['flight_number']}"
        if key not in seen_keys:
            seen_keys.add(key)
            flights.append(flight)

    for row in manual_rows:
        flight = process_flight_row(row)
        dep_date = convert_date(flight["_departure_ts"], flight.get("_dep_tz"))
        key = f"{dep_date}|{flight['departure']['airport_code']}|{flight['arrival']['airport_code']}|{flight['flight_number']}"
        if key not in seen_keys:
            seen_keys.add(key)
            flights.append(flight)

    # Sort by departure time and limit
    flights.sort(key=lambda f: f["_departure_ts"] or 0)
    flights = flights[:limit]

    # Remove internal keys
    for f in flights:
        del f["_departure_ts"]
        f.pop("_dep_tz", None)

    return {"flights": flights, "count": len(flights)}


def get_next_flight(conn):
    """Get the next upcoming flight."""
    result = list_upcoming_flights(conn, limit=1)
    if result["flights"]:
        return {"next_flight": result["flights"][0]}
    return {"next_flight": None, "message": "No upcoming flights found"}


def get_flights_on_date(conn, date_str):
    """Get flights on a specific date (YYYY-MM-DD format).

    Uses a wide UTC window (target date -1 day to +1 day) then filters
    in Python using each flight's departure airport timezone to handle
    international flights correctly.
    """
    cursor = conn.cursor()
    main_user_id = get_main_user_id(conn)

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        # Use wide window to catch all timezone possibilities
        start_ts = (target_date.replace(hour=0, minute=0, second=0)).timestamp() - 86400
        end_ts = (target_date.replace(hour=23, minute=59, second=59)).timestamp() + 86400
    except ValueError:
        return {"error": f"Invalid date format: {date_str}. Use YYYY-MM-DD"}

    flights = []
    superseded_ids = get_superseded_flight_ids(conn)

    # Build user filter
    user_filter = ""
    params = [start_ts, end_ts]
    if main_user_id:
        user_filter = "AND uf.userId = ?"
        params.append(main_user_id)

    # Query tracked flights (exclude superseded)
    cursor.execute(f"""
        SELECT
            a.iata as airline_code,
            f.number as flight_number,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as departure,
            COALESCE(f.lastKnownArrivalDate, f.arrivalScheduleGateOriginal) as arrival,
            t.pnr as confirmation,
            t.seatNumber as seat,
            t.cabinClass as cabin_class,
            COALESCE(at.name, f.equipmentModelName) as aircraft,
            f.equipmentTailNumber as tail_number,
            f.id as flight_id,
            dep.timeZoneIdentifier as dep_tz
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airline a ON f.airlineId = a.id
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.scheduledArrivalAirportId = arr.id
        LEFT JOIN AircraftType at ON f.equipmentModelId = at.id
        LEFT JOIN Ticket t ON f.id = t.flightId AND uf.userId = t.userId
        WHERE uf.isMyFlight = 1
          AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) >= ?
          AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) <= ?
          {user_filter}
        ORDER BY departure
    """, params)

    for row in cursor.fetchall():
        if row[11] in superseded_ids:
            continue
        dep_ts = row[4]
        dep_tz = row[12]
        # Filter by local date at departure airport
        local_date = convert_date(dep_ts, dep_tz)
        if local_date != date_str:
            continue
        flights.append({
            "flight": f"{row[0]} {row[1]}" if row[0] else row[1],
            "route": f"{row[2]} → {row[3]}",
            "departure": format_datetime(dep_ts, dep_tz),
            "arrival": format_datetime(row[5]),
            "confirmation": row[6],
            "seat": row[7],
            "cabin_class": row[8],
            "aircraft": row[9],
            "tail_number": row[10],
            "source": "tracked"
        })

    # Query manual flights (filtered by user)
    manual_user_filter = ""
    manual_params = [start_ts, end_ts]
    if main_user_id:
        manual_user_filter = "AND umf.userId = ?"
        manual_params.append(main_user_id)

    cursor.execute(f"""
        SELECT
            a.iata as airline_code,
            mf.number as flight_number,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            mf.lastKnownDepartureDate as departure,
            mf.lastKnownArrivalDate as arrival,
            COALESCE(at.name, mf.equipmentModelName) as aircraft,
            mf.equipmentTailNumber as tail_number,
            dep.timeZoneIdentifier as dep_tz
        FROM ManualFlight mf
        JOIN UserManualFlight umf ON mf.id = umf.flightId
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.scheduledArrivalAirportId = arr.id
        LEFT JOIN Airline a ON mf.airlineId = a.id
        LEFT JOIN AircraftType at ON mf.equipmentModelId = at.id
        WHERE umf.isMyFlight = 1
          AND umf.deleted IS NULL
          AND mf.lastKnownDepartureDate >= ?
          AND mf.lastKnownDepartureDate <= ?
          {manual_user_filter}
        ORDER BY mf.lastKnownDepartureDate
    """, manual_params)

    for row in cursor.fetchall():
        dep_ts = row[4]
        dep_tz = row[8]
        local_date = convert_date(dep_ts, dep_tz)
        if local_date != date_str:
            continue
        # Manual flight numbers already include the operator prefix
        flights.append({
            "flight": row[1],
            "route": f"{row[2]} → {row[3]}",
            "departure": format_datetime(dep_ts, dep_tz),
            "arrival": format_datetime(row[5]),
            "confirmation": None,
            "seat": None,
            "cabin_class": None,
            "aircraft": row[6],
            "tail_number": row[7],
            "source": "manual"
        })

    return {"date": date_str, "flights": flights, "count": len(flights)}


def search_by_confirmation(conn, pnr):
    """Search flights by confirmation/PNR code."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.iata as airline_code,
            f.number as flight_number,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as departure,
            COALESCE(f.lastKnownArrivalDate, f.arrivalScheduleGateOriginal) as arrival,
            t.pnr as confirmation,
            t.seatNumber as seat,
            t.cabinClass as cabin_class,
            COALESCE(at.name, f.equipmentModelName) as aircraft,
            dep.timeZoneIdentifier as dep_tz
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airline a ON f.airlineId = a.id
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.scheduledArrivalAirportId = arr.id
        LEFT JOIN AircraftType at ON f.equipmentModelId = at.id
        JOIN Ticket t ON f.id = t.flightId AND uf.userId = t.userId
        WHERE t.pnr LIKE ?
        ORDER BY departure
    """, (f"%{pnr}%",))

    flights = []
    for row in cursor.fetchall():
        dep_tz = row[10]
        flights.append({
            "flight": f"{row[0]} {row[1]}",
            "route": f"{row[2]} → {row[3]}",
            "departure": format_datetime(row[4], dep_tz),
            "arrival": format_datetime(row[5]),
            "confirmation": row[6],
            "seat": row[7],
            "cabin_class": row[8],
            "aircraft": row[9]
        })

    return {"confirmation": pnr, "flights": flights, "count": len(flights)}


def get_flight_stats(conn):
    """Get flight statistics from both tables (filtered by primary user)."""
    cursor = conn.cursor()
    now = datetime.now(tz=timezone.utc).timestamp()
    main_user_id = get_main_user_id(conn)

    # Stats from tracked flights
    user_filter = ""
    params = [now]
    if main_user_id:
        user_filter = "AND uf.userId = ?"
        params.append(main_user_id)

    cursor.execute(f"""
        SELECT
            COUNT(*) as total_flights,
            SUM(CASE WHEN COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) > ? THEN 1 ELSE 0 END) as upcoming,
            SUM(f.distance) as total_km
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          {user_filter}
    """, params)
    tracked = cursor.fetchone()

    # Stats from manual flights (filtered by user)
    manual_filter = ""
    manual_params = [now]
    if main_user_id:
        manual_filter = "AND umf.userId = ?"
        manual_params.append(main_user_id)

    cursor.execute(f"""
        SELECT
            COUNT(*) as total_flights,
            SUM(CASE WHEN mf.lastKnownDepartureDate > ? THEN 1 ELSE 0 END) as upcoming,
            SUM(mf.distance) as total_km
        FROM ManualFlight mf
        JOIN UserManualFlight umf ON mf.id = umf.flightId
        WHERE umf.isMyFlight = 1
          AND umf.deleted IS NULL
          {manual_filter}
    """, manual_params)
    manual = cursor.fetchone()

    total_flights = (tracked[0] or 0) + (manual[0] or 0)
    upcoming_flights = (tracked[1] or 0) + (manual[1] or 0)
    total_km = (tracked[2] or 0) + (manual[2] or 0)

    return {
        "total_flights": total_flights,
        "upcoming_flights": upcoming_flights,
        "total_distance_km": total_km,
        "total_distance_miles": int(total_km * 0.621371),
        "earth_circumferences": round(total_km / 40075, 2),
        "tracked_flights": tracked[0] or 0,
        "manual_flights": manual[0] or 0
    }


def get_flights_by_year(conn, year):
    """Get all flights in a given year from both tables.

    Filters out cancelled flights and deduplicates codeshare/reimport entries
    by preferring the entry with a tail number for the same route+date.
    """
    cursor = conn.cursor()
    main_user_id = get_main_user_id(conn)

    start_ts = datetime(year, 1, 1).timestamp()
    end_ts = datetime(year, 12, 31, 23, 59, 59).timestamp()

    flights = []
    # route_key -> flight dict (for route-level dedup that prefers tail numbers)
    route_map = {}

    # Get Flight IDs superseded by ManualFlight entries
    superseded_ids = get_superseded_flight_ids(conn)

    # Query tracked flights (exclude cancelled and superseded)
    user_filter = ""
    params = [start_ts, end_ts]
    if main_user_id:
        user_filter = "AND uf.userId = ? AND uf.importSource != 'CONNECTED_FRIEND'"
        params = [start_ts, end_ts, main_user_id]

    cursor.execute(f"""
        SELECT
            a.iata as airline_code,
            a.name as airline_name,
            f.number as flight_number,
            COALESCE(dep.iata, dep.icao) as dep_code,
            dep.name as dep_airport,
            dep.city as dep_city,
            COALESCE(arr.iata, arr.icao) as arr_code,
            arr.name as arr_airport,
            arr.city as arr_city,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as departure,
            COALESCE(f.lastKnownArrivalDate, f.arrivalScheduleGateOriginal) as arrival,
            t.pnr as confirmation,
            t.seatNumber as seat,
            t.cabinClass as cabin_class,
            COALESCE(at.name, f.equipmentModelName) as aircraft,
            f.departureTerminal as dep_terminal,
            f.departureGate as dep_gate,
            f.arrivalTerminal as arr_terminal,
            f.arrivalGate as arr_gate,
            f.distance as distance_km,
            uf.importSource as import_source,
            f.equipmentTailNumber as tail_number,
            'tracked' as source,
            f.id as flight_id,
            dep.timeZoneIdentifier as dep_tz
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airline a ON f.airlineId = a.id
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.scheduledArrivalAirportId = arr.id
        LEFT JOIN AircraftType at ON f.equipmentModelId = at.id
        LEFT JOIN Ticket t ON f.id = t.flightId AND uf.userId = t.userId
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) >= ?
          AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) <= ?
          {user_filter}
        ORDER BY departure
    """, params)

    for row in cursor.fetchall():
        # Skip flights superseded by ManualFlight entries
        flight_id = row[23]
        if flight_id in superseded_ids:
            continue

        flight = process_flight_row(row)
        dep_date = convert_date(flight["_departure_ts"], flight.get("_dep_tz"))

        # Route-level dedup key: same date + same dep/arr airports
        route_key = f"{dep_date}|{flight['departure']['airport_code']}|{flight['arrival']['airport_code']}"
        has_tail = bool(flight.get("tail_number"))

        if route_key in route_map:
            existing = route_map[route_key]
            existing_has_tail = bool(existing.get("tail_number"))
            # Prefer the entry with a tail number (actually operated)
            if has_tail and not existing_has_tail:
                route_map[route_key] = flight
            # If both have tails (or both don't), keep the first one
        else:
            route_map[route_key] = flight

    # Query manual flights (filtered by user)
    manual_user_filter = ""
    manual_params = [start_ts, end_ts]
    if main_user_id:
        manual_user_filter = "AND umf.userId = ?"
        manual_params.append(main_user_id)

    cursor.execute(f"""
        SELECT
            a.iata as airline_code,
            a.name as airline_name,
            mf.number as flight_number,
            COALESCE(dep.iata, dep.icao) as dep_code,
            dep.name as dep_airport,
            dep.city as dep_city,
            COALESCE(arr.iata, arr.icao) as arr_code,
            arr.name as arr_airport,
            arr.city as arr_city,
            mf.lastKnownDepartureDate as departure,
            mf.lastKnownArrivalDate as arrival,
            NULL as confirmation,
            NULL as seat,
            NULL as cabin_class,
            COALESCE(at.name, mf.equipmentModelName) as aircraft,
            mf.departureTerminal as dep_terminal,
            mf.departureGate as dep_gate,
            mf.arrivalTerminal as arr_terminal,
            mf.arrivalGate as arr_gate,
            mf.distance as distance_km,
            'MANUAL' as import_source,
            mf.equipmentTailNumber as tail_number,
            'manual' as source,
            NULL as flight_id,
            dep.timeZoneIdentifier as dep_tz
        FROM ManualFlight mf
        JOIN UserManualFlight umf ON mf.id = umf.flightId
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.scheduledArrivalAirportId = arr.id
        LEFT JOIN Airline a ON mf.airlineId = a.id
        LEFT JOIN AircraftType at ON mf.equipmentModelId = at.id
        WHERE umf.isMyFlight = 1
          AND umf.deleted IS NULL
          AND mf.lastKnownDepartureDate >= ?
          AND mf.lastKnownDepartureDate <= ?
          {manual_user_filter}
        ORDER BY mf.lastKnownDepartureDate
    """, manual_params)

    for row in cursor.fetchall():
        flight = process_flight_row(row)
        dep_date = convert_date(flight["_departure_ts"], flight.get("_dep_tz"))

        route_key = f"{dep_date}|{flight['departure']['airport_code']}|{flight['arrival']['airport_code']}"
        has_tail = bool(flight.get("tail_number"))

        if route_key in route_map:
            existing = route_map[route_key]
            existing_has_tail = bool(existing.get("tail_number"))
            if has_tail and not existing_has_tail:
                route_map[route_key] = flight
        else:
            route_map[route_key] = flight

    # Build final list from route_map
    flights = list(route_map.values())

    # Sort chronologically
    flights.sort(key=lambda f: f["_departure_ts"] or 0)

    # Compute summary stats
    total_km = sum(f.get("distance_km") or 0 for f in flights)

    # Remove internal keys
    for f in flights:
        del f["_departure_ts"]
        f.pop("_dep_tz", None)

    return {
        "year": year,
        "flights": flights,
        "count": len(flights),
        "total_distance_km": total_km,
        "total_distance_miles": int(total_km * 0.621371) if total_km else 0
    }


def get_recent_flights(conn, limit=20):
    """Get recent/past flights from both tables (filtered by primary user)."""
    cursor = conn.cursor()
    now = datetime.now(tz=timezone.utc).timestamp()
    main_user_id = get_main_user_id(conn)
    superseded_ids = get_superseded_flight_ids(conn)

    flights = []

    # Build user filter
    user_filter = ""
    params = [now]
    if main_user_id:
        user_filter = "AND uf.userId = ?"
        params.append(main_user_id)

    # Query tracked flights (exclude superseded)
    cursor.execute(f"""
        SELECT
            a.iata as airline_code,
            f.number as flight_number,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as departure,
            COALESCE(at.name, f.equipmentModelName) as aircraft,
            f.distance as distance_km,
            f.equipmentTailNumber as tail_number,
            'tracked' as source,
            f.id as flight_id,
            dep.timeZoneIdentifier as dep_tz
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airline a ON f.airlineId = a.id
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.scheduledArrivalAirportId = arr.id
        LEFT JOIN AircraftType at ON f.equipmentModelId = at.id
        WHERE uf.isMyFlight = 1
          AND uf.deleted IS NULL
          AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) < ?
          {user_filter}
        ORDER BY departure DESC
        LIMIT ?
    """, params + [limit * 2])

    for row in cursor.fetchall():
        if row[9] in superseded_ids:
            continue
        dep_tz = row[10]
        flights.append({
            "flight": f"{row[0]} {row[1]}" if row[0] else row[1],
            "route": f"{row[2]} → {row[3]}",
            "date": convert_date(row[4], dep_tz),
            "aircraft": row[5],
            "distance_km": row[6],
            "tail_number": row[7],
            "source": row[8],
            "_ts": row[4]
        })

    # Query manual flights (filtered by user)
    manual_filter = ""
    manual_params = [now]
    if main_user_id:
        manual_filter = "AND umf.userId = ?"
        manual_params.append(main_user_id)

    cursor.execute(f"""
        SELECT
            a.iata as airline_code,
            mf.number as flight_number,
            COALESCE(dep.iata, dep.icao) as dep_code,
            COALESCE(arr.iata, arr.icao) as arr_code,
            mf.lastKnownDepartureDate as departure,
            COALESCE(at.name, mf.equipmentModelName) as aircraft,
            mf.distance as distance_km,
            mf.equipmentTailNumber as tail_number,
            'manual' as source,
            dep.timeZoneIdentifier as dep_tz
        FROM ManualFlight mf
        JOIN UserManualFlight umf ON mf.id = umf.flightId
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.scheduledArrivalAirportId = arr.id
        LEFT JOIN Airline a ON mf.airlineId = a.id
        LEFT JOIN AircraftType at ON mf.equipmentModelId = at.id
        WHERE umf.isMyFlight = 1
          AND umf.deleted IS NULL
          AND mf.lastKnownDepartureDate < ?
          {manual_filter}
        ORDER BY mf.lastKnownDepartureDate DESC
        LIMIT ?
    """, manual_params + [limit * 2])

    for row in cursor.fetchall():
        dep_tz = row[9]
        # Manual flight numbers already include the operator prefix
        flights.append({
            "flight": row[1],
            "route": f"{row[2]} → {row[3]}",
            "date": convert_date(row[4], dep_tz),
            "aircraft": row[5],
            "distance_km": row[6],
            "tail_number": row[7],
            "source": row[8],
            "_ts": row[4]
        })

    # Sort by date descending and limit
    flights.sort(key=lambda f: f["_ts"] or 0, reverse=True)
    flights = flights[:limit]

    # Remove internal sort key
    for f in flights:
        del f["_ts"]

    return {"recent_flights": flights, "count": len(flights)}


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: query_flights.py <command> [args]"}))
        sys.exit(1)

    command = sys.argv[1] if not sys.argv[1].startswith("--") else "list"

    # Check database
    db_path, error = get_db_path()
    if error:
        print(json.dumps({"error": error}))
        sys.exit(1)

    # Execute command
    try:
        conn = sqlite3.connect(db_path)

        if command == "list" or command == "--list":
            limit = 20
            include_friends = False
            for arg in sys.argv[2:]:
                if arg == "--include-friends":
                    include_friends = True
                elif arg.isdigit():
                    limit = int(arg)
            result = list_upcoming_flights(conn, limit, include_friends)
        elif command == "next" or command == "--next":
            result = get_next_flight(conn)
        elif command == "date" or command == "--date":
            if len(sys.argv) < 3:
                result = {"error": "Usage: query_flights.py date YYYY-MM-DD"}
            else:
                result = get_flights_on_date(conn, sys.argv[2])
        elif command == "pnr" or command == "--pnr":
            if len(sys.argv) < 3:
                result = {"error": "Usage: query_flights.py pnr <confirmation_code>"}
            else:
                result = search_by_confirmation(conn, sys.argv[2])
        elif command == "stats" or command == "--stats":
            result = get_flight_stats(conn)
        elif command == "year" or command == "--year":
            if len(sys.argv) < 3:
                result = {"error": "Usage: query_flights.py year YYYY"}
            else:
                try:
                    year = int(sys.argv[2])
                    result = get_flights_by_year(conn, year)
                except ValueError:
                    result = {"error": f"Invalid year: {sys.argv[2]}. Use YYYY format"}
        elif command == "recent" or command == "--recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            result = get_recent_flights(conn, limit)
        else:
            result = {"error": f"Unknown command: {command}. Use: list, next, date, year, pnr, stats, recent"}

        conn.close()
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
