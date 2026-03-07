from pathlib import Path
from app.utils import save_to_json

import requests
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "Aviation Incident API"}
PARAMS = {
    "action": "parse",
    "page": "List of accidents and incidents involving commercial aircraft",
    "format": "json",
}

def fetch_incident_links(url: str, path: Path) -> list[dict]:
    response = requests.get(url, headers=HEADERS, params=PARAMS)
    response.raise_for_status()

    html = response.json()["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="mw-parser-output")

    links = []
    for li in content.select("ul > li"):
        a = li.find("a", href=True)
        if not a:
            continue

        href = a["href"]
        if href.startswith("/wiki/Timeline"):
            break

        if (
            href.startswith("/wiki/")
            and ":" not in href
            and not href.startswith(("/wiki/List_", "/wiki/Lists"))
        ):
            print(href)
            links.append({
                "Name": href.removeprefix("/wiki/").replace("_", " "),
                "Link": f"https://en.wikipedia.org{href}",
            })
    save_to_json(links, path)
    return links