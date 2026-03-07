from pathlib import Path

from scrape_incident_details import extract_incident_details
from scrape_incident_links import fetch_incident_links

BASE_DIR = Path(__file__).resolve().parent.parent

LINK_FILE = BASE_DIR / "data" / "aviation_incident_links.json"
DETAIL_FILE = BASE_DIR / "data" / "aviation_incident_details.json"
URL = "https://en.wikipedia.org/w/api.php"

def main():
    incident_links = fetch_incident_links(URL, LINK_FILE)
    detail_list = extract_incident_details(incident_links, DETAIL_FILE)

if __name__ == "__main__":
    main()


