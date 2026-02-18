#!/usr/bin/env python3
"""
Query Tripsy database for trip information.
Outputs structured JSON for easy parsing by Claude.
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Tripsy database location (macOS)
DEFAULT_DB_PATH = Path.home() / "Library/Group Containers/group.app.tripsy.ios/Tripsy.sqlite"

# Core Data epoch offset (Jan 1, 2001 vs Jan 1, 1970)
CORE_DATA_OFFSET = 978307200


def get_db_path():
    """Get database path, checking if it exists."""
    # Use default path - commands are passed as arguments, not db path
    db_path = DEFAULT_DB_PATH
    if not db_path.exists():
        return None, f"Database not found at {db_path}"
    return db_path, None


def convert_timestamp(ts):
    """Convert Core Data timestamp to ISO format."""
    if ts is None:
        return None
    unix_ts = ts + CORE_DATA_OFFSET
    return datetime.fromtimestamp(unix_ts).isoformat()


def convert_date(ts):
    """Convert Core Data timestamp to date string."""
    if ts is None:
        return None
    unix_ts = ts + CORE_DATA_OFFSET
    return datetime.fromtimestamp(unix_ts).strftime("%Y-%m-%d")


def days_until(ts):
    """Calculate days until a timestamp."""
    if ts is None:
        return None
    unix_ts = ts + CORE_DATA_OFFSET
    target = datetime.fromtimestamp(unix_ts)
    delta = target - datetime.now()
    return delta.days


def list_upcoming_trips(conn, limit=20):
    """List all upcoming trips."""
    cursor = conn.cursor()
    now_core_data = datetime.now().timestamp() - CORE_DATA_OFFSET

    cursor.execute("""
        SELECT
            ZINTERNALIDENTIFIER as id,
            ZNAME as name,
            ZSTARTS as starts,
            ZENDS as ends,
            ZNOTES as notes
        FROM ZTRIP
        WHERE ZENDS > ?
        ORDER BY ZSTARTS
        LIMIT ?
    """, (now_core_data, limit))

    trips = []
    for row in cursor.fetchall():
        trips.append({
            "id": row[0],
            "name": row[1],
            "starts": convert_date(row[2]),
            "ends": convert_date(row[3]),
            "days_until": days_until(row[2]),
            "duration_days": (row[3] - row[2]) // 86400 if row[2] and row[3] else None,
            "notes": row[4]
        })

    return {"trips": trips, "count": len(trips)}


def get_trip_details(conn, trip_name):
    """Get full details for a specific trip including flights, hotels, activities."""
    cursor = conn.cursor()
    now_core_data = datetime.now().timestamp() - CORE_DATA_OFFSET

    # Find the trip
    cursor.execute("""
        SELECT ZINTERNALIDENTIFIER, ZNAME, ZSTARTS, ZENDS, ZNOTES
        FROM ZTRIP
        WHERE ZNAME LIKE ? AND ZENDS > ?
        ORDER BY ZSTARTS
        LIMIT 1
    """, (f"%{trip_name}%", now_core_data))

    trip_row = cursor.fetchone()
    if not trip_row:
        return {"error": f"No upcoming trip found matching '{trip_name}'"}

    trip = {
        "id": trip_row[0],
        "name": trip_row[1],
        "starts": convert_date(trip_row[2]),
        "ends": convert_date(trip_row[3]),
        "days_until": days_until(trip_row[2]),
        "notes": trip_row[4]
    }

    trip_start = trip_row[2]
    trip_end = trip_row[3]

    # Get flights (with 1 day buffer)
    cursor.execute("""
        SELECT
            ZCOMPANY as airline,
            ZTRANSPORTNUMBER as flight_number,
            ZDEPARTURE as departure,
            ZARRIVAL as arrival,
            ZDEPARTUREADDRESS as from_location,
            ZARRIVALADDRESS as to_location,
            ZRESERVATIONCODE as confirmation,
            ZINTERNALTYPE as type
        FROM ZTRANSPORTATION
        WHERE ZDEPARTURE >= ? - 86400 AND ZDEPARTURE <= ? + 86400
        ORDER BY ZDEPARTURE
    """, (trip_start, trip_end))

    flights = []
    for row in cursor.fetchall():
        flights.append({
            "airline": row[0],
            "flight_number": row[1],
            "departure": convert_timestamp(row[2]),
            "arrival": convert_timestamp(row[3]),
            "from": row[4],
            "to": row[5],
            "confirmation": row[6],
            "type": row[7]
        })

    # Get hotels
    cursor.execute("""
        SELECT
            ZNAME as name,
            ZADDRESS as address,
            ZSTARTS as checkin,
            ZENDS as checkout,
            ZRESERVATIONCODE as confirmation,
            ZROOMTYPE as room_type,
            ZPHONE as phone
        FROM ZHOSTING
        WHERE ZSTARTS >= ? - 86400 AND ZSTARTS <= ? + 86400
        ORDER BY ZSTARTS
    """, (trip_start, trip_end))

    hotels = []
    for row in cursor.fetchall():
        hotels.append({
            "name": row[0],
            "address": row[1],
            "checkin": convert_timestamp(row[2]),
            "checkout": convert_timestamp(row[3]),
            "confirmation": row[4],
            "room_type": row[5],
            "phone": row[6]
        })

    # Get activities
    cursor.execute("""
        SELECT
            ZNAME as name,
            ZSTARTS as datetime,
            ZADDRESS as location,
            ZRESERVATIONCODE as confirmation,
            ZINTERNALTYPE as type,
            ZNOTES as notes
        FROM ZACTIVITY
        WHERE ZSTARTS >= ? AND ZSTARTS <= ?
        ORDER BY ZSTARTS
    """, (trip_start, trip_end))

    activities = []
    for row in cursor.fetchall():
        activities.append({
            "name": row[0],
            "datetime": convert_timestamp(row[1]),
            "location": row[2],
            "confirmation": row[3],
            "type": row[4],
            "notes": row[5]
        })

    return {
        "trip": trip,
        "flights": flights,
        "hotels": hotels,
        "activities": activities
    }


def get_next_flights(conn, limit=10):
    """Get upcoming flights."""
    cursor = conn.cursor()
    now_core_data = datetime.now().timestamp() - CORE_DATA_OFFSET

    cursor.execute("""
        SELECT
            ZCOMPANY as airline,
            ZTRANSPORTNUMBER as flight_number,
            ZDEPARTURE as departure,
            ZARRIVAL as arrival,
            ZDEPARTUREADDRESS as from_location,
            ZARRIVALADDRESS as to_location,
            ZRESERVATIONCODE as confirmation,
            ZINTERNALTYPE as type
        FROM ZTRANSPORTATION
        WHERE ZINTERNALTYPE = 'airplane' AND ZDEPARTURE > ?
        ORDER BY ZDEPARTURE
        LIMIT ?
    """, (now_core_data, limit))

    flights = []
    for row in cursor.fetchall():
        flights.append({
            "airline": row[0],
            "flight_number": row[1],
            "departure": convert_timestamp(row[2]),
            "arrival": convert_timestamp(row[3]),
            "from": row[4],
            "to": row[5],
            "confirmation": row[6],
            "type": row[7]
        })

    return {"flights": flights, "count": len(flights)}


def get_next_hotels(conn, limit=5):
    """Get upcoming hotel stays."""
    cursor = conn.cursor()
    now_core_data = datetime.now().timestamp() - CORE_DATA_OFFSET

    cursor.execute("""
        SELECT
            ZNAME as name,
            ZADDRESS as address,
            ZSTARTS as checkin,
            ZENDS as checkout,
            ZRESERVATIONCODE as confirmation,
            ZROOMTYPE as room_type
        FROM ZHOSTING
        WHERE ZSTARTS > ?
        ORDER BY ZSTARTS
        LIMIT ?
    """, (now_core_data, limit))

    hotels = []
    for row in cursor.fetchall():
        hotels.append({
            "name": row[0],
            "address": row[1],
            "checkin": convert_timestamp(row[2]),
            "checkout": convert_timestamp(row[3]),
            "confirmation": row[4],
            "room_type": row[5],
            "days_until": days_until(row[2])
        })

    return {"hotels": hotels, "count": len(hotels)}


def main():
    """Main entry point."""
    # Parse command
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: query_trips.py <command> [args]"}))
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
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            result = list_upcoming_trips(conn, limit)
        elif command == "trip" or command == "--trip":
            if len(sys.argv) < 3:
                result = {"error": "Usage: query_trips.py trip <trip_name>"}
            else:
                trip_name = " ".join(sys.argv[2:])
                result = get_trip_details(conn, trip_name)
        elif command == "flights" or command == "--flights":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            result = get_next_flights(conn, limit)
        elif command == "hotels" or command == "--hotels":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            result = get_next_hotels(conn, limit)
        else:
            result = {"error": f"Unknown command: {command}. Use: list, trip, flights, hotels"}

        conn.close()
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
