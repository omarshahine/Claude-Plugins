#!/usr/bin/env python3
"""
Search Google Flights for airfare pricing using the fast-flights library.
Outputs structured JSON for easy parsing by Claude.

Usage:
    python search_flights.py search --from SEA --to HKG --date 2025-06-15 [options]
    python search_flights.py multi --legs "SEA,HKG,2025-06-15;HKG,PEK,2025-06-20;PEK,SEA,2025-06-25" [options]

Options:
    --seat economy|premium-economy|business|first (default: economy)
    --adults N (default: 1)
    --children N (default: 0)
    --trip one-way|round-trip (for search command, default: one-way)
    --return-date YYYY-MM-DD (for round-trip searches)
    --fetch-mode common|fallback|local (default: fallback)

Trip Types:
    one-way: Single flight from A to B
    round-trip: Outbound A→B and return B→A (specify --return-date)
    multi-city: Multiple legs (use 'multi' command with --legs)
"""

import argparse
import json
import sys
from typing import Optional

try:
    from fast_flights import FlightData, Passengers, get_flights
except ImportError:
    print(json.dumps({
        "error": "fast-flights library not installed. Install with: pip install fast-flights"
    }))
    sys.exit(1)


def format_flight(flight) -> dict:
    """Convert a Flight object to a dictionary."""
    return {
        "airline": flight.name,
        "departure": flight.departure,
        "arrival": flight.arrival,
        "duration": flight.duration,
        "stops": flight.stops,
        "price": flight.price,
        "is_best": getattr(flight, 'is_best', False),
        "delay": getattr(flight, 'delay', None),
        "arrival_time_ahead": getattr(flight, 'arrival_time_ahead', None),
    }


def search_flights(
    from_airport: str,
    to_airport: str,
    date: str,
    return_date: Optional[str] = None,
    seat: str = "economy",
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0,
    trip_type: str = "one-way",
    fetch_mode: str = "fallback"
) -> dict:
    """Search for flights between two airports."""

    # Build flight data
    flight_data = [FlightData(date=date, from_airport=from_airport, to_airport=to_airport)]

    # For round-trip, add return leg
    if trip_type == "round-trip" and return_date:
        flight_data.append(FlightData(date=return_date, from_airport=to_airport, to_airport=from_airport))
        trip = "round-trip"
    else:
        trip = "one-way"

    # Build passengers
    passengers = Passengers(
        adults=adults,
        children=children,
        infants_in_seat=infants_in_seat,
        infants_on_lap=infants_on_lap
    )

    try:
        result = get_flights(
            flight_data=flight_data,
            trip=trip,
            seat=seat,
            passengers=passengers,
            fetch_mode=fetch_mode
        )

        flights = [format_flight(f) for f in result.flights]

        return {
            "search": {
                "from": from_airport,
                "to": to_airport,
                "date": date,
                "return_date": return_date,
                "trip_type": trip,
                "seat_class": seat,
                "passengers": {
                    "adults": adults,
                    "children": children,
                    "infants_in_seat": infants_in_seat,
                    "infants_on_lap": infants_on_lap,
                    "total": adults + children + infants_in_seat + infants_on_lap
                }
            },
            "price_level": getattr(result, 'current_price', None),
            "flights": flights,
            "count": len(flights)
        }
    except Exception as e:
        error_msg = str(e)
        if "Connect" in error_msg or "tunnel" in error_msg:
            error_msg = "Network connection failed. Check internet connectivity."
        return {"error": error_msg, "search": {
            "from": from_airport,
            "to": to_airport,
            "date": date
        }}


def search_multi_city(
    legs: list[tuple[str, str, str]],
    seat: str = "economy",
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0,
    fetch_mode: str = "fallback"
) -> dict:
    """Search for multi-city flights.

    Args:
        legs: List of (from_airport, to_airport, date) tuples
        seat: Cabin class
        adults, children, etc.: Passenger counts
        fetch_mode: How to fetch data (common, fallback, local)
    """

    # Build flight data for each leg
    flight_data = [
        FlightData(date=date, from_airport=from_apt, to_airport=to_apt)
        for from_apt, to_apt, date in legs
    ]

    # Build passengers
    passengers = Passengers(
        adults=adults,
        children=children,
        infants_in_seat=infants_in_seat,
        infants_on_lap=infants_on_lap
    )

    # Format legs for output (do this first for error reporting)
    legs_info = [
        {"from": from_apt, "to": to_apt, "date": date}
        for from_apt, to_apt, date in legs
    ]

    try:
        result = get_flights(
            flight_data=flight_data,
            trip="multi-city",
            seat=seat,
            passengers=passengers,
            fetch_mode=fetch_mode
        )

        flights = [format_flight(f) for f in result.flights]

        return {
            "search": {
                "type": "multi-city",
                "legs": legs_info,
                "seat_class": seat,
                "passengers": {
                    "adults": adults,
                    "children": children,
                    "infants_in_seat": infants_in_seat,
                    "infants_on_lap": infants_on_lap,
                    "total": adults + children + infants_in_seat + infants_on_lap
                }
            },
            "price_level": getattr(result, 'current_price', None),
            "flights": flights,
            "count": len(flights)
        }
    except Exception as e:
        error_msg = str(e)
        if "Connect" in error_msg or "tunnel" in error_msg:
            error_msg = "Network connection failed. Check internet connectivity."
        return {"error": error_msg, "search": {"type": "multi-city", "legs": legs_info}}


def parse_legs(legs_str: str) -> list[tuple[str, str, str]]:
    """Parse legs string format: 'FROM,TO,DATE;FROM,TO,DATE;...'"""
    legs = []
    for leg in legs_str.split(";"):
        parts = leg.strip().split(",")
        if len(parts) != 3:
            raise ValueError(f"Invalid leg format: {leg}. Expected 'FROM,TO,DATE'")
        legs.append((parts[0].strip().upper(), parts[1].strip().upper(), parts[2].strip()))
    return legs


def main():
    parser = argparse.ArgumentParser(description="Search Google Flights for airfare pricing")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search command (one-way or round-trip)
    search_parser = subparsers.add_parser("search", help="Search for flights")
    search_parser.add_argument("--from", dest="from_airport", required=True, help="Departure airport code")
    search_parser.add_argument("--to", dest="to_airport", required=True, help="Arrival airport code")
    search_parser.add_argument("--date", required=True, help="Departure date (YYYY-MM-DD)")
    search_parser.add_argument("--return-date", help="Return date for round-trip (YYYY-MM-DD)")
    search_parser.add_argument("--trip", choices=["one-way", "round-trip"], default="one-way", help="Trip type")
    search_parser.add_argument("--seat", choices=["economy", "premium-economy", "business", "first"], default="economy")
    search_parser.add_argument("--adults", type=int, default=1)
    search_parser.add_argument("--children", type=int, default=0)
    search_parser.add_argument("--infants-in-seat", type=int, default=0)
    search_parser.add_argument("--infants-on-lap", type=int, default=0)
    search_parser.add_argument("--fetch-mode", choices=["common", "fallback", "local"], default="fallback",
                               help="How to fetch data: common (direct), fallback (with retry), local (playwright)")

    # Multi-city command
    multi_parser = subparsers.add_parser("multi", help="Search multi-city flights")
    multi_parser.add_argument("--legs", required=True, help="Flight legs: 'FROM,TO,DATE;FROM,TO,DATE;...'")
    multi_parser.add_argument("--seat", choices=["economy", "premium-economy", "business", "first"], default="economy")
    multi_parser.add_argument("--adults", type=int, default=1)
    multi_parser.add_argument("--children", type=int, default=0)
    multi_parser.add_argument("--infants-in-seat", type=int, default=0)
    multi_parser.add_argument("--infants-on-lap", type=int, default=0)
    multi_parser.add_argument("--fetch-mode", choices=["common", "fallback", "local"], default="fallback",
                               help="How to fetch data: common (direct), fallback (with retry), local (playwright)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print(json.dumps({"error": "No command specified. Use 'search' or 'multi'"}))
        sys.exit(1)

    if args.command == "search":
        result = search_flights(
            from_airport=args.from_airport.upper(),
            to_airport=args.to_airport.upper(),
            date=args.date,
            return_date=args.return_date,
            seat=args.seat,
            adults=args.adults,
            children=args.children,
            infants_in_seat=args.infants_in_seat,
            infants_on_lap=args.infants_on_lap,
            trip_type=args.trip if args.trip else ("round-trip" if args.return_date else "one-way"),
            fetch_mode=args.fetch_mode
        )
    elif args.command == "multi":
        try:
            legs = parse_legs(args.legs)
        except ValueError as e:
            print(json.dumps({"error": str(e)}))
            sys.exit(1)

        result = search_multi_city(
            legs=legs,
            seat=args.seat,
            adults=args.adults,
            children=args.children,
            infants_in_seat=args.infants_in_seat,
            infants_on_lap=args.infants_on_lap,
            fetch_mode=args.fetch_mode
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
