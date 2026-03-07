import math
from collections import Counter
from pathlib import Path as FilePath
from typing import Any
from datetime import datetime

from fastapi import FastAPI, Path
from fastapi.params import Query

BASE_DIR = FilePath(__file__).resolve().parent.parent
DETAIL_FILE = BASE_DIR / "data" / "aviation_incident_details.json"
incident_list = []
if DETAIL_FILE.exists():
    try:
        from utils import load_from_json
        raw_data = load_from_json(DETAIL_FILE)
        incident_list = [i for i in raw_data if not i.get('error')]
    except Exception as e:
        print(f"Error loading JSON: {e}")
else:
    print(f"Warning: Data file not found at {DETAIL_FILE}")
app = FastAPI(
    title="Aviation Incidents API",
    version="1.0"
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Aviation Incident API",
        "developed_by": {
            "name": "Pranjal Jais",
            "email": "pranjaljais2@gmail.com",
            "instagram": "https://www.instagram.com/pranjaljais13",
            "github": "https://github.com/pranjal0jais",
        },
        "documentation": "/docs"
    }

@app.get("/api/incidents",
         description="Get all incidents from Aviation Incidents API")
def get_incident_details(
        offset: int = Query(0, ge=0),
        limit: int = Query(default=10, le=100)
) -> dict[str,Any]:
    total = len(incident_list)
    data = incident_list[offset:offset+limit]
    return {
        "total": total,
        "data": data,
        "limit": limit,
        "offset": offset,
    }

@app.get("/api/incidents/country/{country_name}",
         description="Get all incidents from a specific country")
def get_incidents_by_country(
        country_name: str,
        limit: int = Query(default=10, le=100),
        offset: int = Query(0, ge=0)
)->dict[str,Any]:
    country_name = country_name.lower()
    filtered_list = [incident for incident in incident_list
                     if country_name in str(incident.get('Site', {}).get('Country', "")).lower()]
    data = filtered_list[offset:offset+limit]
    return {
        "total": len(filtered_list),
        "data": data,
        "limit": limit,
        "offset": offset,
    }

@app.get("/api/incidents/timeline",
         description="Get all incidents from a specific timeline(years)")
def get_incidents_timeline_interval(
        start_year: int = Query(default=1900, ge=1900, le=datetime.now().year),
        end_year:int = Query(default=datetime.now().year, le=datetime.now().year),
        limit: int = Query(default=10, le=100),
        offset: int = Query(0, ge=0)
) -> dict[str,Any]:
    if start_year > end_year:
        return {"error": "start_year cannot be greater than end_year", "data": []}
    filtered_list = []

    for incident in incident_list:
        date_str = incident.get('Date')
        if not date_str:
            continue

        try:
            year = int(date_str[0:4])
            if start_year <= year <= end_year:
                filtered_list.append(incident)
        except(ValueError, IndexError):
            continue

    data = filtered_list[offset:offset+limit]
    return {
        "total": len(filtered_list),
        "data": data,
        "limit": limit,
        "offset": offset,
    }

@app.get("/api/incidents/year/{year}",
         description="Get all incidents from a specific year")
def get_incidents_by_year(
        year: int = Path(..., ge=1900, le=datetime.now().year),
        limit: int = Query(default=10, le=100),
        offset: int = Query(0, ge=0)
)->dict[str,Any]:
    filtered_list = []
    for incident in incident_list:
        date_str = incident.get('Date')
        if not date_str:
            continue
        try:
            year_val = int(date_str.split("-")[0])
            if year == year_val:
                filtered_list.append(incident)
        except(ValueError, IndexError):
            continue

    data = filtered_list[offset:offset+limit]
    return {
        "total": len(filtered_list),
        "data": data,
        "limit": limit,
        "offset": offset,
    }


def calculate_distance(lat1, lon1, lat2, lon2):
    # Earth's radius in kilometers
    R = 6371.0

    # Convert degrees to radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # Haversine calculation
    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(dlambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

@app.get("/api/incidents/nearby",
         description="Get all nearby incidents within a specified radius")
def get_nearby_incidents(
        lat: float = Query(..., ge=-90, le=90),
        lon: float = Query(..., ge=-180, le=180),
        radius_km: float = Query(default=100, gt=0),
        limit: int = 10
)->dict[str,Any]:
    filtered_list = []
    for incident in incident_list:
        coords = incident.get('Site', {}).get('Coordinates', None)
        if coords is None:
            continue

        lat_val = float(coords.get('Lat', None))
        lon_val = float(coords.get('Long', None))
        if lat_val is None or lon_val is None:
            continue

        distance = calculate_distance(lat, lon, lat_val, lon_val)

        if distance <= radius_km:
            temp = incident.copy()
            temp['Distance_km'] = round(distance, 2)
            filtered_list.append(temp)
    filtered_list.sort(key=lambda x: x["Distance_km"])
    return {
        "center": {"lat": lat, "lon": lon},
        "radius": radius_km,
        "total_found": len(filtered_list),
        "data": filtered_list[:limit]
    }

@app.get("/api/incidents/aircraft/summary",
         description="Get Count of incidents by aircraft")
def get_aircraft_summary(
        limit: int = Query(default=10, le=100)
)->dict[str,Any]:

    aircraft_list = [incident.get("Aircraft type", "Unknown") for incident in incident_list]
    counts = Counter(aircraft_list).most_common(limit)

    return {
        "limit": limit,
        "summary": [{"Aircraft type": aircraft_type, "Count": count}
                    for aircraft_type, count in counts]
    }