import requests


def _element_coords(element):
    """Get lat/lon from an Overpass element."""
    if "lat" in element and "lon" in element:
        return element["lat"], element["lon"]
    center = element.get("center", {})
    return center.get("lat"), center.get("lon")


def _element_name(tags, fallback="Unknown"):
    """Get a readable name from OSM tags."""
    return tags.get("name") or tags.get("operator") or fallback


def fetch_nearby_sources(lat, lon, radius_m=5000):
    """Query Overpass API for pollution-relevant nearby landmarks."""
    try:
        query = f"""
        [out:json][timeout:25];
        (
          node["landuse"="industrial"](around:{radius_m},{lat},{lon});
          way["landuse"="industrial"](around:{radius_m},{lat},{lon});
          node["man_made"="works"](around:{radius_m},{lat},{lon});
          way["man_made"="works"](around:{radius_m},{lat},{lon});
          node["building"="factory"](around:{radius_m},{lat},{lon});
          way["building"="factory"](around:{radius_m},{lat},{lon});
          node["construction"="yes"](around:{radius_m},{lat},{lon});
          way["construction"="yes"](around:{radius_m},{lat},{lon});
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
          node["amenity"="school"](around:{radius_m},{lat},{lon});
        );
        out center;
        """
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=10,
        )
        response.raise_for_status()
        elements = response.json().get("elements", [])

        industries = []
        hospitals = []
        schools = []
        construction = []

        for element in elements:
            tags = element.get("tags", {})
            elat, elon = _element_coords(element)
            if elat is None or elon is None:
                continue

            name = _element_name(tags)
            entry = {"name": name, "lat": elat, "lon": elon}

            if tags.get("landuse") == "industrial":
                industries.append({**entry, "type": "industrial_area"})
            elif tags.get("man_made") == "works" or tags.get("building") == "factory":
                industries.append({**entry, "type": "factory"})
            elif tags.get("construction") == "yes":
                construction.append(entry)
            elif tags.get("amenity") == "hospital":
                hospitals.append(entry)
            elif tags.get("amenity") == "school":
                schools.append(entry)

        return {
            "industries": industries,
            "hospitals": hospitals,
            "schools": schools,
            "construction": construction,
        }
    except Exception:
        return {
            "industries": [],
            "hospitals": [],
            "schools": [],
            "construction": [],
        }
