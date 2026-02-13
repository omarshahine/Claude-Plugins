#!/usr/bin/env python3
"""Generate a self-contained HTML flight tracker map.

Usage:
    python3 flight-map.py N464QS              # Generate map and open in browser
    python3 flight-map.py N464QS --output map.html  # Save to file
    python3 flight-map.py N464QS --no-open    # Generate but don't open browser

The generated HTML auto-refreshes by re-running this script via a meta refresh,
or can be used as a static snapshot.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import webbrowser
from datetime import datetime, timezone

# Get the directory of this script so we can find flight-radar.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FLIGHT_RADAR = os.path.join(SCRIPT_DIR, "flight-radar.py")


def get_flight_data(tail):
    """Run flight-radar.py and parse the JSON output."""
    result = subprocess.run(
        [sys.executable, FLIGHT_RADAR, tail, "--json"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def generate_html(data, tail):
    """Generate a self-contained Leaflet map HTML page."""
    if not data or data.get("status") == "not_found":
        return f"""<!DOCTYPE html>
<html><head><title>{tail} - Not Found</title>
<style>body{{font-family:system-ui;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#1a1a2e;color:#e0e0e0}}
.card{{background:#16213e;padding:40px;border-radius:12px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.3)}}
h1{{color:#ff6b6b;margin-bottom:8px}}p{{color:#a0a0a0}}</style></head>
<body><div class="card"><h1>{tail}</h1><p>Not currently tracked on FlightRadar24.</p>
<p style="font-size:13px;margin-top:20px">Aircraft may be parked or transponder is off.</p></div></body></html>"""

    lat = data.get("latitude", 0)
    lon = data.get("longitude", 0)
    reg = data.get("registration", tail)
    cs = data.get("callsign", "")
    model = data.get("aircraft_model") or data.get("aircraft_type", "")
    airline = data.get("airline", "")
    origin = data.get("origin", "???")
    origin_city = data.get("origin_city", "")
    dest = data.get("destination", "???")
    dest_city = data.get("destination_city", "")
    alt = data.get("altitude_ft", 0) or 0
    speed = data.get("ground_speed_kts", 0) or 0
    heading = data.get("heading", 0) or 0
    on_ground = data.get("on_ground", False)
    status = data.get("flight_status", "")
    dep = data.get("actual_departure", "")
    arr = data.get("actual_arrival", "")
    eta = data.get("eta", "")

    # Build recent flights HTML
    history_html = ""
    recent = data.get("recent_flights", [])
    if recent:
        rows = ""
        for h in recent:
            ho = h.get("origin", "?")
            hoc = h.get("origin_city", "")
            hd = h.get("destination", "?")
            hdc = h.get("destination_city", "")
            hdep = h.get("departure", "")
            rows += f"<tr><td>{hdep}</td><td>{ho} ({hoc})</td><td>{hd} ({hdc})</td></tr>"
        history_html = f"""<div class="history">
<h3>Recent Flights</h3>
<table><thead><tr><th>Departed</th><th>From</th><th>To</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""

    ground_badge = '<span class="badge ground">ON GROUND</span>' if on_ground else '<span class="badge air">IN FLIGHT</span>'
    status_line = f'<span class="status-text">{status}</span>' if status else ""

    zoom = 6 if not on_ground and alt > 10000 else 10 if not on_ground else 13
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{reg} - Live Flight Tracker</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: system-ui, -apple-system, sans-serif; background: #0f0f23; color: #e0e0e0; }}
#map {{ height: 65vh; width: 100%; }}
.info-panel {{
  padding: 16px 20px;
  background: #1a1a2e;
  border-top: 2px solid #16213e;
}}
.info-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  max-width: 1200px;
  margin: 0 auto;
}}
.info-item {{ padding: 8px 0; }}
.info-label {{ font-size: 11px; text-transform: uppercase; color: #666; letter-spacing: 0.5px; }}
.info-value {{ font-size: 16px; font-weight: 600; color: #e0e0e0; margin-top: 2px; }}
.header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #16213e;
}}
.header h1 {{ font-size: 20px; font-weight: 700; }}
.header h1 span {{ color: #888; font-weight: 400; font-size: 14px; margin-left: 8px; }}
.badge {{
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.badge.ground {{ background: #2d6a4f; color: #95d5b2; }}
.badge.air {{ background: #1d3557; color: #a8dadc; }}
.status-text {{ color: #a8dadc; font-size: 13px; margin-left: 8px; }}
.timestamp {{ font-size: 11px; color: #555; }}
.route {{
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.route .arrow {{ color: #555; }}
.route .code {{ color: #e0e0e0; }}
.route .city {{ color: #888; font-size: 12px; font-weight: 400; }}
.history {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 20px;
  border-top: 1px solid #16213e;
}}
.history h3 {{ font-size: 13px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
.history table {{ width: 100%; font-size: 13px; border-collapse: collapse; }}
.history th {{ text-align: left; color: #555; font-weight: 500; padding: 4px 8px; }}
.history td {{ padding: 4px 8px; color: #aaa; }}
.history tr:hover td {{ color: #e0e0e0; }}
</style>
</head>
<body>
<div class="header">
  <h1>{reg}<span>{model}{(' - ' + airline) if airline else ''}</span></h1>
  <div>{ground_badge} {status_line}</div>
</div>
<div id="map"></div>
<div class="info-panel">
  <div class="info-grid">
    <div class="info-item">
      <div class="info-label">Route</div>
      <div class="route">
        <span class="code">{origin}</span><span class="city">{origin_city}</span>
        <span class="arrow">&rarr;</span>
        <span class="code">{dest}</span><span class="city">{dest_city}</span>
      </div>
    </div>
    <div class="info-item">
      <div class="info-label">Altitude</div>
      <div class="info-value">{alt:,} ft</div>
    </div>
    <div class="info-item">
      <div class="info-label">Ground Speed</div>
      <div class="info-value">{speed} kts</div>
    </div>
    <div class="info-item">
      <div class="info-label">Heading</div>
      <div class="info-value">{heading}&deg;</div>
    </div>
    <div class="info-item">
      <div class="info-label">Departed</div>
      <div class="info-value">{dep or 'N/A'}</div>
    </div>
    <div class="info-item">
      <div class="info-label">{'Arrived' if arr else 'ETA'}</div>
      <div class="info-value">{arr or eta or 'N/A'}</div>
    </div>
  </div>
</div>
{history_html}
<div style="text-align:center;padding:8px"><span class="timestamp">Generated {now}</span></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const lat = {lat};
const lon = {lon};
const heading = {heading};
const onGround = {'true' if on_ground else 'false'};

const map = L.map('map', {{
  center: [lat, lon],
  zoom: {zoom},
  zoomControl: true
}});

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap &copy; CARTO',
  maxZoom: 19
}}).addTo(map);

// Aircraft icon as rotated SVG
const planeIcon = L.divIcon({{
  html: `<svg width="32" height="32" viewBox="0 0 24 24" style="transform:rotate(${{heading}}deg);filter:drop-shadow(0 0 4px rgba(168,218,220,0.6))">
    <path d="M12 2L8 10H3L5 12L3 14H8L12 22L16 14H21L19 12L21 10H16L12 2Z"
          fill="${{onGround ? '#95d5b2' : '#a8dadc'}}" stroke="#16213e" stroke-width="0.5"/>
  </svg>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  className: ''
}});

L.marker([lat, lon], {{ icon: planeIcon }}).addTo(map)
  .bindPopup(`<b>{reg}</b><br>{cs} - {model}<br>{origin} &rarr; {dest}`);
</script>
</body>
</html>"""


def main():
    p = argparse.ArgumentParser(description="Generate a flight tracker map")
    p.add_argument("tail", help="Tail number (e.g. N464QS)")
    p.add_argument("--output", "-o", help="Output HTML file path")
    p.add_argument("--no-open", action="store_true", help="Don't open in browser")
    args = p.parse_args()

    data = get_flight_data(args.tail)
    html = generate_html(data, args.tail)

    if args.output:
        path = args.output
    else:
        fd, path = tempfile.mkstemp(suffix=".html", prefix=f"flight-{args.tail}-")
        os.close(fd)

    with open(path, "w") as f:
        f.write(html)

    print(f"Map saved to: {path}")

    if not args.no_open:
        webbrowser.open(f"file://{os.path.abspath(path)}")


if __name__ == "__main__":
    main()
