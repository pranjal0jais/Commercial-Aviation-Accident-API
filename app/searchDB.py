from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.filedb.filestore import RamStorage

schema = Schema(
    id=ID(unique=True, stored=True),
    Title=TEXT(stored=True),
    Location=TEXT(stored=True),
    Summary=TEXT(stored=True),
    Aircraft_Name=TEXT(stored=True),
    Aircraft_Type=TEXT(stored=True)
)

def build_index(incidents: list[dict]) -> index.Index:
    st = RamStorage()
    ix = st.create_index(schema)
    writer = ix.writer()
    for i, incident in enumerate(incidents):
        writer.add_document(
            id=str(i),
            Title=incident.get("Title") or "",
            Location=incident.get("Site", {}).get("RawLocation") or "",
            Summary=incident.get("Summary") or "",
            Aircraft_Name=incident.get("Aircraft Name") or "",
            Aircraft_Type=incident.get("Aircraft type") or ""
        )
    writer.commit()
    print(f"Whoosh indexed {len(incidents)} incidents")
    return ix