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
from datetime import datetime
from pathlib import Path

# Flighty database location (macOS)
DEFAULT_DB_PATH = Path.home() / "Library/Containers/com.flightyapp.flighty/Data/Documents/MainFlightyDatabase.db"


def get_db_path():
    """Get database path, checking if it exists."""
    db_path = DEFAULT_DB_PATH
    if not db_path.exists():
        return None, f"Database not found at {db_path}"
    return db_path, None


def convert_timestamp(ts):
    """Convert Unix timestamp to ISO format (local time)."""
    if ts is None:
        return None
    return datetime.fromtimestamp(ts).isoformat()


def convert_date(ts):
    """Convert Unix timestamp to date string."""
    if ts is None:
        return None
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def format_datetime(ts):
    """Format timestamp for display."""
    if ts is None:
        return None
    return datetime.fromtimestamp(ts).strftime("%b %d, %Y %I:%M %p")


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
    target = datetime.fromtimestamp(ts)
    delta = target - datetime.now()
    return delta.days


def get_main_user_id(conn):
    """Identify the main user (not a connected friend)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT userId
        FROM UserFlight
        WHERE importSource != 'CONNECTED_FRIEND' AND importSource IS NOT NULL AND importSource != ''
        GROUP BY userId
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    return row[0] if row else None


def query_tracked_upcoming(conn, now, main_user_id, include_friends, limit):
    """Query tracked flights (Flight table) for upcoming flights."""
    cursor = conn.cursor()

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
            dep.iata as dep_code,
            dep.name as dep_airport,
            dep.city as dep_city,
            arr.iata as arr_code,
            arr.name as arr_airport,
            arr.city as arr_city,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as departure,
            COALESCE(f.lastKnownArrivalDate, f.arrivalScheduleGateOriginal) as arrival,
            t.pnr as confirmation,
            t.seatNumber as seat,
            t.cabinClass as cabin_class,
            f.equipmentModelName as aircraft,
            f.departureTerminal as dep_terminal,
            f.departureGate as dep_gate,
            f.arrivalTerminal as arr_terminal,
            f.arrivalGate as arr_gate,
            f.distance as distance_km,
            uf.importSource as import_source,
            f.equipmentTailNumber as tail_number,
            'tracked' as source
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airline a ON f.airlineId = a.id
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.actualArrivalAirportId = arr.id
        LEFT JOIN Ticket t ON f.id = t.flightId AND uf.userId = t.userId
        WHERE {where_clause}
        ORDER BY departure
        LIMIT ?
    """, params + [limit * 2])  # Fetch extra to allow for merging

    return cursor.fetchall()


def query_manual_upcoming(conn, now, limit):
    """Query manual flights (ManualFlight table) for upcoming flights."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            NULL as airline_code,
            NULL as airline_name,
            mf.number as flight_number,
            dep.iata as dep_code,
            dep.name as dep_airport,
            dep.city as dep_city,
            arr.iata as arr_code,
            arr.name as arr_airport,
            arr.city as arr_city,
            mf.lastKnownDepartureDate as departure,
            mf.lastKnownArrivalDate as arrival,
            NULL as confirmation,
            NULL as seat,
            NULL as cabin_class,
            mf.equipmentModelName as aircraft,
            mf.departureTerminal as dep_terminal,
            mf.departureGate as dep_gate,
            mf.arrivalTerminal as arr_terminal,
            mf.arrivalGate as arr_gate,
            mf.distance as distance_km,
            'MANUAL' as import_source,
            mf.equipmentTailNumber as tail_number,
            'manual' as source
        FROM ManualFlight mf
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.actualArrivalAirportId = arr.id
        WHERE mf.lastKnownDepartureDate > ?
        ORDER BY mf.lastKnownDepartureDate
        LIMIT ?
    """, (now, limit * 2))

    return cursor.fetchall()


def process_flight_row(row):
    """Process a flight row into a dictionary."""
    cabin_class = row[13]
    if cabin_class:
        cabin_display = cabin_class.replace("premiumEconomy", "Premium Economy").replace("privateJet", "Private Jet").title()
    else:
        cabin_display = None

    departure_ts = row[9]
    arrival_ts = row[10]

    return {
        "flight": f"{row[0]} {row[2]}" if row[0] and row[2] else row[2],
        "airline": row[1],
        "flight_number": row[2],
        "route": f"{row[3]} → {row[6]}",
        "departure": {
            "airport_code": row[3],
            "airport_name": row[4],
            "city": row[5],
            "datetime": convert_timestamp(departure_ts),
            "display": format_datetime(departure_ts),
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
        "_departure_ts": departure_ts  # For sorting
    }


def list_upcoming_flights(conn, limit=20, include_friends=False):
    """List all upcoming flights with full details from both tables."""
    now = datetime.now().timestamp()
    main_user_id = get_main_user_id(conn)

    # Get flights from both tables
    tracked_rows = query_tracked_upcoming(conn, now, main_user_id, include_friends, limit)
    manual_rows = query_manual_upcoming(conn, now, limit)

    # Process and combine
    flights = []
    seen_keys = set()

    for row in tracked_rows:
        flight = process_flight_row(row)
        # Dedup key: date + route + flight number
        dep_date = convert_date(flight["_departure_ts"])
        key = f"{dep_date}|{flight['departure']['airport_code']}|{flight['arrival']['airport_code']}|{flight['flight_number']}"
        if key not in seen_keys:
            seen_keys.add(key)
            flights.append(flight)

    for row in manual_rows:
        flight = process_flight_row(row)
        dep_date = convert_date(flight["_departure_ts"])
        key = f"{dep_date}|{flight['departure']['airport_code']}|{flight['arrival']['airport_code']}|{flight['flight_number']}"
        if key not in seen_keys:
            seen_keys.add(key)
            flights.append(flight)

    # Sort by departure time and limit
    flights.sort(key=lambda f: f["_departure_ts"] or 0)
    flights = flights[:limit]

    # Remove internal sort key
    for f in flights:
        del f["_departure_ts"]

    return {"flights": flights, "count": len(flights)}


def get_next_flight(conn):
    """Get the next upcoming flight."""
    result = list_upcoming_flights(conn, limit=1)
    if result["flights"]:
        return {"next_flight": result["flights"][0]}
    return {"next_flight": None, "message": "No upcoming flights found"}


def get_flights_on_date(conn, date_str):
    """Get flights on a specific date (YYYY-MM-DD format)."""
    cursor = conn.cursor()

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        start_ts = target_date.timestamp()
        end_ts = (target_date.replace(hour=23, minute=59, second=59)).timestamp()
    except ValueError:
        return {"error": f"Invalid date format: {date_str}. Use YYYY-MM-DD"}

    flights = []

    # Query tracked flights
    cursor.execute("""
        SELECT
            a.iata as airline_code,
            f.number as flight_number,
            dep.iata as dep_code,
            arr.iata as arr_code,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as departure,
            COALESCE(f.lastKnownArrivalDate, f.arrivalScheduleGateOriginal) as arrival,
            t.pnr as confirmation,
            t.seatNumber as seat,
            t.cabinClass as cabin_class,
            f.equipmentModelName as aircraft,
            f.equipmentTailNumber as tail_number
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airline a ON f.airlineId = a.id
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.actualArrivalAirportId = arr.id
        LEFT JOIN Ticket t ON f.id = t.flightId AND uf.userId = t.userId
        WHERE uf.isMyFlight = 1
          AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) >= ?
          AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) <= ?
        ORDER BY departure
    """, (start_ts, end_ts))

    for row in cursor.fetchall():
        flights.append({
            "flight": f"{row[0]} {row[1]}" if row[0] else row[1],
            "route": f"{row[2]} → {row[3]}",
            "departure": format_datetime(row[4]),
            "arrival": format_datetime(row[5]),
            "confirmation": row[6],
            "seat": row[7],
            "cabin_class": row[8],
            "aircraft": row[9],
            "tail_number": row[10],
            "source": "tracked"
        })

    # Query manual flights
    cursor.execute("""
        SELECT
            mf.number as flight_number,
            dep.iata as dep_code,
            arr.iata as arr_code,
            mf.lastKnownDepartureDate as departure,
            mf.lastKnownArrivalDate as arrival,
            mf.equipmentModelName as aircraft,
            mf.equipmentTailNumber as tail_number
        FROM ManualFlight mf
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.actualArrivalAirportId = arr.id
        WHERE mf.lastKnownDepartureDate >= ?
          AND mf.lastKnownDepartureDate <= ?
        ORDER BY mf.lastKnownDepartureDate
    """, (start_ts, end_ts))

    for row in cursor.fetchall():
        flights.append({
            "flight": row[0],
            "route": f"{row[1]} → {row[2]}",
            "departure": format_datetime(row[3]),
            "arrival": format_datetime(row[4]),
            "confirmation": None,
            "seat": None,
            "cabin_class": None,
            "aircraft": row[5],
            "tail_number": row[6],
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
            dep.iata as dep_code,
            arr.iata as arr_code,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as departure,
            COALESCE(f.lastKnownArrivalDate, f.arrivalScheduleGateOriginal) as arrival,
            t.pnr as confirmation,
            t.seatNumber as seat,
            t.cabinClass as cabin_class,
            f.equipmentModelName as aircraft
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airline a ON f.airlineId = a.id
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.actualArrivalAirportId = arr.id
        JOIN Ticket t ON f.id = t.flightId AND uf.userId = t.userId
        WHERE t.pnr LIKE ?
        ORDER BY departure
    """, (f"%{pnr}%",))

    flights = []
    for row in cursor.fetchall():
        flights.append({
            "flight": f"{row[0]} {row[1]}",
            "route": f"{row[2]} → {row[3]}",
            "departure": format_datetime(row[4]),
            "arrival": format_datetime(row[5]),
            "confirmation": row[6],
            "seat": row[7],
            "cabin_class": row[8],
            "aircraft": row[9]
        })

    return {"confirmation": pnr, "flights": flights, "count": len(flights)}


def get_flight_stats(conn):
    """Get flight statistics from both tables."""
    cursor = conn.cursor()
    now = datetime.now().timestamp()

    # Stats from tracked flights
    cursor.execute("""
        SELECT
            COUNT(*) as total_flights,
            SUM(CASE WHEN COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) > ? THEN 1 ELSE 0 END) as upcoming,
            SUM(f.distance) as total_km
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        WHERE uf.isMyFlight = 1
    """, (now,))
    tracked = cursor.fetchone()

    # Stats from manual flights
    cursor.execute("""
        SELECT
            COUNT(*) as total_flights,
            SUM(CASE WHEN lastKnownDepartureDate > ? THEN 1 ELSE 0 END) as upcoming,
            SUM(distance) as total_km
        FROM ManualFlight
    """, (now,))
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


def get_recent_flights(conn, limit=20):
    """Get recent/past flights from both tables."""
    cursor = conn.cursor()
    now = datetime.now().timestamp()

    flights = []

    # Query tracked flights
    cursor.execute("""
        SELECT
            a.iata as airline_code,
            f.number as flight_number,
            dep.iata as dep_code,
            arr.iata as arr_code,
            COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) as departure,
            f.equipmentModelName as aircraft,
            f.distance as distance_km,
            f.equipmentTailNumber as tail_number,
            'tracked' as source
        FROM Flight f
        JOIN UserFlight uf ON f.id = uf.flightId
        JOIN Airline a ON f.airlineId = a.id
        JOIN Airport dep ON f.departureAirportId = dep.id
        JOIN Airport arr ON f.actualArrivalAirportId = arr.id
        WHERE uf.isMyFlight = 1
          AND uf.isArchived = 0
          AND COALESCE(f.lastKnownDepartureDate, f.departureScheduleGateOriginal) < ?
        ORDER BY departure DESC
        LIMIT ?
    """, (now, limit * 2))

    for row in cursor.fetchall():
        flights.append({
            "flight": f"{row[0]} {row[1]}" if row[0] else row[1],
            "route": f"{row[2]} → {row[3]}",
            "date": convert_date(row[4]),
            "aircraft": row[5],
            "distance_km": row[6],
            "tail_number": row[7],
            "source": row[8],
            "_ts": row[4]
        })

    # Query manual flights
    cursor.execute("""
        SELECT
            mf.number as flight_number,
            dep.iata as dep_code,
            arr.iata as arr_code,
            mf.lastKnownDepartureDate as departure,
            mf.equipmentModelName as aircraft,
            mf.distance as distance_km,
            mf.equipmentTailNumber as tail_number,
            'manual' as source
        FROM ManualFlight mf
        JOIN Airport dep ON mf.departureAirportId = dep.id
        JOIN Airport arr ON mf.actualArrivalAirportId = arr.id
        WHERE mf.lastKnownDepartureDate < ?
        ORDER BY mf.lastKnownDepartureDate DESC
        LIMIT ?
    """, (now, limit * 2))

    for row in cursor.fetchall():
        flights.append({
            "flight": row[0],
            "route": f"{row[1]} → {row[2]}",
            "date": convert_date(row[3]),
            "aircraft": row[4],
            "distance_km": row[5],
            "tail_number": row[6],
            "source": row[7],
            "_ts": row[3]
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
        elif command == "recent" or command == "--recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            result = get_recent_flights(conn, limit)
        else:
            result = {"error": f"Unknown command: {command}. Use: list, next, date, pnr, stats, recent"}

        conn.close()
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
