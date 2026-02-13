#!/usr/bin/env python3
"""Track aircraft by tail number using FlightRadar24 API.

Usage:
    python3 flight-radar.py N464QS              # Track a specific tail
    python3 flight-radar.py N464QS N479QS       # Multiple tails
    python3 flight-radar.py N464QS --poll 30    # Poll every 30 seconds
    python3 flight-radar.py --fleet EJA         # All active flights for an airline
    python3 flight-radar.py N464QS --json       # Raw JSON output
    python3 flight-radar.py --fleet EJA --json  # Fleet as JSON
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone

from FlightRadar24 import FlightRadar24API

fr = FlightRadar24API()


def format_timestamp(ts):
    """Convert Unix timestamp to readable string."""
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def flight_to_dict(f):
    """Convert a Flight object to a clean dictionary."""
    return {
        "callsign": getattr(f, 'callsign', None),
        "registration": getattr(f, 'registration', None),
        "aircraft_type": getattr(f, 'aircraft_code', None),
        "latitude": getattr(f, 'latitude', None),
        "longitude": getattr(f, 'longitude', None),
        "altitude_ft": getattr(f, 'altitude', None),
        "ground_speed_kts": getattr(f, 'ground_speed', None),
        "heading": getattr(f, 'heading', None),
        "origin": getattr(f, 'origin_airport_iata', None),
        "destination": getattr(f, 'destination_airport_iata', None),
        "on_ground": getattr(f, 'on_ground', None),
    }


def enrich_with_details(f, d):
    """Call get_flight_details() to add aircraft model, airline, airport names,
    timing, and recent flight history to the result dict."""
    details = fr.get_flight_details(f)
    if not details:
        return

    if "aircraft" in details:
        ac = details["aircraft"]
        if "model" in ac:
            d["aircraft_model"] = ac["model"].get("text")
            d["aircraft_type"] = ac["model"].get("code", d.get("aircraft_type"))
        d["hex"] = ac.get("hex")

    if "airline" in details:
        al = details["airline"]
        d["airline"] = al.get("name")
        d["airline_icao"] = al.get("code", {}).get("icao")

    if "airport" in details:
        ap = details["airport"]
        if "origin" in ap and ap["origin"]:
            o = ap["origin"]
            d["origin_name"] = o.get("name")
            d["origin_city"] = o.get("position", {}).get("region", {}).get("city")
        if "destination" in ap and ap["destination"]:
            dest = ap["destination"]
            d["destination_name"] = dest.get("name")
            d["destination_city"] = dest.get("position", {}).get("region", {}).get("city")

    if "status" in details:
        d["flight_status"] = details["status"].get("text")

    if "time" in details:
        t = details["time"]
        if "scheduled" in t:
            d["scheduled_departure"] = format_timestamp(t["scheduled"].get("departure"))
            d["scheduled_arrival"] = format_timestamp(t["scheduled"].get("arrival"))
        if "real" in t:
            d["actual_departure"] = format_timestamp(t["real"].get("departure"))
            d["actual_arrival"] = format_timestamp(t["real"].get("arrival"))
        if "other" in t and t["other"].get("eta"):
            d["eta"] = format_timestamp(t["other"]["eta"])

    if "flightHistory" in details and "aircraft" in details["flightHistory"]:
        history = []
        for h in details["flightHistory"]["aircraft"]:
            entry = {
                "callsign": h.get("identification", {}).get("number", {}).get("default"),
            }
            hap = h.get("airport", {})
            if "origin" in hap and hap["origin"]:
                entry["origin"] = hap["origin"]["code"].get("iata")
                entry["origin_city"] = hap["origin"].get("position", {}).get("region", {}).get("city")
            if "destination" in hap and hap["destination"]:
                entry["destination"] = hap["destination"]["code"].get("iata")
                entry["destination_city"] = hap["destination"].get("position", {}).get("region", {}).get("city")
            dep_ts = h.get("time", {}).get("real", {}).get("departure")
            entry["departure"] = format_timestamp(dep_ts)
            history.append(entry)
        d["recent_flights"] = history


def get_airline_fleet(airline_icao):
    """Return all active flights for an airline by ICAO code."""
    return [flight_to_dict(f) for f in fr.get_flights(airline=airline_icao)]


def main():
    p = argparse.ArgumentParser(description="Track aircraft via FlightRadar24")
    p.add_argument("tails", nargs="*", help="Tail numbers (e.g. N464QS)")
    p.add_argument("--fleet", type=str, metavar="ICAO", help="Show all active flights for airline ICAO code (e.g. EJA, UAL, DAL)")
    p.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    p.add_argument("--poll", type=int, default=0, help="Poll interval in seconds (0=once)")
    args = p.parse_args()

    if not args.tails and not args.fleet:
        p.print_help()
        sys.exit(1)

    while True:
        results = []

        if args.fleet:
            fleet = get_airline_fleet(args.fleet)
            if args.as_json:
                results.extend(fleet)
            else:
                print(f"Active {args.fleet} flights: {len(fleet)}")
                for f in sorted(fleet, key=lambda x: x.get('callsign') or ''):
                    reg = f['registration'] or 'N/A'
                    cs = f['callsign'] or 'N/A'
                    org = f['origin'] or '???'
                    dst = f['destination'] or '???'
                    alt = f['altitude_ft'] or 0
                    spd = f['ground_speed_kts'] or 0
                    lat = f['latitude'] or 0
                    lon = f['longitude'] or 0
                    print(f"  {cs:10s} {reg:8s} {org}->{dst}  {alt:,}ft  {spd}kts  ({lat:.2f}, {lon:.2f})")

        for tail in args.tails:
            # Use registration filter (faster than scanning all flights)
            flights = fr.get_flights(registration=tail.upper())
            flight = flights[0] if flights else None

            if flight is None:
                entry = {"tail": tail, "status": "not_found",
                         "message": "Not currently airborne or not tracked"}
                if args.as_json:
                    results.append(entry)
                else:
                    print(f"{tail}: Not currently airborne or not tracked")
                continue

            d = flight_to_dict(flight)
            d["status"] = "tracked"
            enrich_with_details(flight, d)

            if args.as_json:
                results.append(d)
            else:
                model = d.get('aircraft_model') or d['aircraft_type'] or '?'
                airline = d.get('airline') or ''
                status = d.get('flight_status') or ''
                alt = d['altitude_ft'] or 0
                spd = d['ground_speed_kts'] or 0
                org = d['origin'] or '???'
                dst = d['destination'] or '???'
                org_city = d.get('origin_city') or ''
                dst_city = d.get('destination_city') or ''
                lat = d['latitude'] or 0
                lon = d['longitude'] or 0
                hdg = d['heading'] or 0
                ground = " (ON GROUND)" if d['on_ground'] else ""

                print(f"{d['registration']} ({d['callsign']}) - {model}")
                if airline:
                    print(f"  Airline:  {airline}")
                print(f"  Route:    {org} ({org_city}) -> {dst} ({dst_city})")
                print(f"  Position: {lat:.4f}, {lon:.4f}  Heading: {hdg}")
                print(f"  Altitude: {alt:,} ft  Speed: {spd} kts{ground}")
                if status:
                    print(f"  Status:   {status}")
                if d.get('actual_departure'):
                    print(f"  Departed: {d['actual_departure']}")
                if d.get('actual_arrival'):
                    print(f"  Arrived:  {d['actual_arrival']}")
                elif d.get('eta'):
                    print(f"  ETA:      {d['eta']}")

                if d.get('recent_flights'):
                    print(f"  Recent flights:")
                    for h in d['recent_flights']:
                        ho = h.get('origin', '???')
                        hd = h.get('destination', '???')
                        hoc = h.get('origin_city') or ''
                        hdc = h.get('destination_city') or ''
                        dep = h.get('departure') or '?'
                        print(f"    {dep}  {ho} ({hoc}) -> {hd} ({hdc})")

        if args.as_json and results:
            print(json.dumps(results if len(results) > 1 else results[0], indent=2))

        if args.poll <= 0:
            break
        time.sleep(args.poll)


if __name__ == "__main__":
    main()
