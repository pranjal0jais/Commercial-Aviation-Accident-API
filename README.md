# ✈️ Aviation Incidents API

A FastAPI-powered REST API that serves historical aviation incident data scraped from Wikipedia. Built with a custom web scraper and backed by structured JSON data, it lets you query incidents by country, year, timeline, proximity, and aircraft type.

---

## 📁 Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & route definitions
│   └── utils.py         # JSON load/save helpers
├── scraper/
│   ├── __init__.py
│   ├── scraper.py               # Entry point for scraping
│   ├── scrape_incident_links.py # Fetches incident URLs from Wikipedia
│   └── scrape_incident_details.py # Scrapes detail pages
├── data/
│   ├── aviation_incident_links.json   # Raw list of incident links
│   └── aviation_incident_details.json # Enriched incident records
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/pranjal0jais/aviation-incidents-api.git
cd aviation-incidents-api
pip install -r requirements.txt
```

### Running the Scraper

Before starting the API, populate the data directory by running the scraper:

```bash
cd scraper
python scraper.py
```

This will:
1. Fetch all aviation incident links from Wikipedia
2. Scrape individual detail pages for each incident
3. Save results to `data/aviation_incident_details.json`

### Starting the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

---

## 📡 API Endpoints

### `GET /`
Returns a welcome message and developer info.

---

### `GET /api/incidents`
Returns a paginated list of all incidents.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `offset` | int | `0` | Number of records to skip |
| `limit` | int | `10` | Max records to return (≤ 100) |

---

### `GET /api/incidents/country/{country_name}`
Returns incidents filtered by country name (case-insensitive partial match).

| Param | Type | Description |
|---|---|---|
| `country_name` | path | Country to filter by |
| `limit` | query | Max results (≤ 100) |
| `offset` | query | Pagination offset |

---

### `GET /api/incidents/year/{year}`
Returns all incidents from a specific year.

| Param | Type | Description |
|---|---|---|
| `year` | path | Year between 1900 and current year |
| `limit` | query | Max results (≤ 100) |
| `offset` | query | Pagination offset |

---

### `GET /api/incidents/timeline`
Returns incidents within a year range.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `start_year` | int | `1900` | Start of range |
| `end_year` | int | current year | End of range |
| `limit` | int | `10` | Max results (≤ 100) |
| `offset` | int | `0` | Pagination offset |

---

### `GET /api/incidents/nearby`
Returns incidents within a given radius of a geographic coordinate.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `lat` | float | required | Latitude (-90 to 90) |
| `lon` | float | required | Longitude (-180 to 180) |
| `radius_km` | float | `100` | Search radius in kilometers |
| `limit` | int | `10` | Max results |

Results are sorted by distance from the provided coordinates.

---

### `GET /api/incidents/aircraft/summary`
Returns a ranked count of incidents by aircraft type.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | `10` | Number of aircraft types to return (≤ 100) |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML parsing |
| [Requests](https://docs.python-requests.org/) | HTTP scraping |
| [Pandas](https://pandas.pydata.org/) | Date parsing |

---

## 👤 Developer

**Pranjal Jais**  
📧 pranjaljais2@gmail.com  
📸 [@pranjaljais13](https://www.instagram.com/pranjaljais13)  
🐙 [github.com/pranjal0jais](https://github.com/pranjal0jais)

---

## 📄 License

This project uses data sourced from [Wikipedia](https://en.wikipedia.org) under the [Creative Commons Attribution-ShareAlike License](https://creativecommons.org/licenses/by-sa/3.0/).
