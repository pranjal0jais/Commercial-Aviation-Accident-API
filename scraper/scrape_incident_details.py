from pathlib import Path
from time import sleep
import re
import pandas as pd

import requests
from bs4 import BeautifulSoup
from app.utils import load_from_json, save_to_json

HEADERS = {"User-Agent": "Aviation Incident API"}
DELAY = 0.5
NUMERIC_FIELDS = ["Survivors", "Injuries", "Fatalities", "Crew", "Passengers"]

def extract_incident_details(data: list, path: Path):
    existing = load_from_json(path)

    normalized = []
    for item in existing:
        if isinstance(item, list):
            normalized.append({"Link": item[0], "info": item[1]})
        else:
            normalized.append(item)

    done_titles = {item["Link"] for item in normalized if "Link" in item}
    detailed_data = normalized

    remaining = [d for d in data if d["Link"] not in done_titles]
    total = len(remaining)
    print(f"Already done: {len(detailed_data)} | Remaining: {total}")

    for i, incident in enumerate(remaining):
        try:
            print(f"[{i + 1}/{total}] {incident['Name']}")
            response = requests.get(incident["Link"], headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            received_data = extract_data(soup)
            received_data["Link"] = incident["Link"]
            detailed_data.append(received_data)

            if (i + 1) % 10 == 0:
                save_to_json(detailed_data, path)
                print(f"Progress saved: {len(detailed_data)} records")

            sleep(DELAY)

        except Exception as e:
            print(f"Failed: {incident['Name']} — {e}")
            detailed_data.append({"Title": incident["Name"], "Info": [], "error": str(e)})
            continue

    save_to_json(detailed_data, path)
    print(f"Done! Total records: {len(detailed_data)}")
    return detailed_data

def extract_data(soup):
    title = soup.find("title").get_text(strip=True).replace("- Wikipedia", "").strip()
    table = soup.find("table", class_="infobox")
    incident = dict()
    if table is None:
        return {"Title": title, "info": []}

    info = []
    for row in table.find_all("tr"):
        header = row.find("th", class_="infobox-label")
        value_td = row.find("td", class_="infobox-data")

        if not (header and value_td):
            continue

        key = header.get_text(strip=True)
        text = value_td.get_text(" ", strip=True)

        if key == "Site":
            value = extract_site(value_td)

        elif key == "Date":
            value = extract_date(value_td)

        elif key in NUMERIC_FIELDS:
            value = parse_number(text, mode="first")

        elif key == "Occupants":
            value = parse_number(text, mode="sum")

        else:
            value = text

        incident[key] = value
    incident["Title"] = title
    return incident


def extract_site(td):
    plainlist = td.find("div", class_="plainlist")
    if not plainlist:
        raw_location = td.get_text(" ", strip=True)
    else:
        first_li = plainlist.find("li")
        raw_location = first_li.get_text(" ", strip=True)\
            if first_li \
            else td.get_text(" ",strip=True)
    parts = [p.strip() for p in raw_location.split(",") if p.strip()]

    country = parts[-1] if parts else "Unknown"
    locality = ", ".join(parts[:-1]) if len(parts) > 1 else parts[0] if parts else ""

    coordinates = None
    geo = td.find("span", class_="geo")
    if geo:
        coords = geo.get_text(strip=True).split(";")
        if len(coords) == 2:
            coordinates = {"Lat": coords[0].strip(), "Long": coords[1].strip()}

    return {
        "RawLocation": raw_location,
        "Location": locality,
        "Country": country,
        "Coordinates": coordinates
    }

def parse_number(text, mode="first"):
    if not text:
        return None

    text = text.lower().strip()

    if text in ["unknown", "n/a", "none", "-", "–"]:
        return None

    numbers = [int(n) for n in re.findall(r"\d+", text)]

    if not numbers:
        return None

    if mode == "first":
        return numbers[0]

    if mode == "sum":
        return sum(numbers)

    if mode == "max":
        return max(numbers)

    return numbers[0]

def extract_date(td):
    spans = td.find_all("span")
    date_text = spans[1].get_text(strip=True) if len(spans) > 1 else td.get_text(strip=True)

    date_text = re.sub(r"\[.*?\]", "", date_text)

    date_text = re.sub(r"\(.*?\)", "", date_text)

    date_text = re.sub(r"\d{1,2}:\d{2}.*", "", date_text)

    date_text = date_text.replace("Z", "")

    date_text = re.split(r"–|-", date_text)[0]

    date_text = date_text.strip()
    date = pd.to_datetime(date_text, errors="ignore")
    return date.strftime("%Y-%m-%d")
