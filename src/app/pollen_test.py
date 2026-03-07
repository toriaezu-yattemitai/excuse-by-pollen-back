import json
import os
from pathlib import Path
from typing import Any, TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

POLLEN_API_URL = "https://pollen.googleapis.com/v1/forecast:lookup"
GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"

APP_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = APP_ROOT / ".env"
INPUT_JSON_PATH = Path(__file__).resolve().parent / "data" / "dummy_prompt_request.json"

LANGUAGE_CODE = "ja"
DAYS = 1

PollenResult = TypedDict(
    "PollenResult",
    {
        "location": str,
        "pollen-index": str,
        "pollen-species": str,
    },
)


def load_api_key() -> str:
    load_dotenv(dotenv_path=ENV_PATH)
    api_key = os.getenv("POLLEN_API_KEY")
    if not api_key:
        raise RuntimeError("POLLEN_API_KEY is not set. Please add it to .env.")
    return api_key


def load_payload(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_coordinates(payload: dict[str, Any]) -> tuple[float, float]:
    options = payload.get("options")
    if not isinstance(options, dict):
        raise ValueError("options is missing in input json.")

    location = options.get("location")
    if not isinstance(location, dict):
        raise ValueError("options.location is missing in input json.")

    latitude = location.get("latitude")
    longitude = location.get("longitude")

    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        raise ValueError("options.location.latitude/longitude must be numeric.")

    return float(latitude), float(longitude)


def fetch_json(url: str, params: dict[str, str]) -> dict[str, Any]:
    request = Request(f"{url}?{urlencode(params)}", method="GET")
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"API request failed: {error.code} {body}") from error
    except URLError as error:
        raise RuntimeError(f"API request failed: {error.reason}") from error


def fetch_pollen_forecast(api_key: str, latitude: float, longitude: float) -> dict[str, Any]:
    params = {
        "location.latitude": str(latitude),
        "location.longitude": str(longitude),
        "days": str(DAYS),
        "languageCode": LANGUAGE_CODE,
        "plantsDescription": "true",
        "key": api_key,
    }
    return fetch_json(POLLEN_API_URL, params)


def reverse_geocode_city(api_key: str, latitude: float, longitude: float) -> str:
    params = {
        "latlng": f"{latitude},{longitude}",
        "language": "ja",
        "key": api_key,
        # 住所系だけに少し絞る
        "result_type": (
            "locality|administrative_area_level_2|"
            "administrative_area_level_3|administrative_area_level_1"
        ),
    }
    payload = fetch_json(GEOCODING_API_URL, params)

    if payload.get("status") != "OK":
        return "unknown"

    results = payload.get("results", [])
    if not isinstance(results, list) or not results:
        return "unknown"

    # 欲しい粒度の優先順
    priority_types = [
        "locality",                      # 市区町村
        "administrative_area_level_2",  # 市・郡
        "administrative_area_level_3",  # 町・村など
    ]

    for target_type in priority_types:
        for result in results:
            if not isinstance(result, dict):
                continue

            address_components = result.get("address_components", [])
            if not isinstance(address_components, list):
                continue

            for comp in address_components:
                if not isinstance(comp, dict):
                    continue

                comp_types = comp.get("types", [])
                if target_type in comp_types:
                    name = comp.get("long_name")
                    if isinstance(name, str) and name.strip():
                        return name.strip()

    # 市区町村が取れなければ都道府県
    for result in results:
        if not isinstance(result, dict):
            continue

        address_components = result.get("address_components", [])
        if not isinstance(address_components, list):
            continue

        for comp in address_components:
            if not isinstance(comp, dict):
                continue

            comp_types = comp.get("types", [])
            if "administrative_area_level_1" in comp_types:
                name = comp.get("long_name")
                if isinstance(name, str) and name.strip():
                    return name.strip()

    # 最後の保険
    formatted_address = results[0].get("formatted_address")
    if isinstance(formatted_address, str) and formatted_address.strip():
        return formatted_address.strip()

    return "unknown"


def summarize_forecast(pollen_payload: dict[str, Any], location_name: str) -> PollenResult:
    daily_info = pollen_payload.get("dailyInfo")
    if not isinstance(daily_info, list) or not daily_info:
        raise ValueError("dailyInfo is missing in Pollen API response.")

    today = daily_info[0]

    pollen_type_info = today.get("pollenTypeInfo")
    if not isinstance(pollen_type_info, list):
        pollen_type_info = []

    values: list[int] = []
    for item in pollen_type_info:
        if not isinstance(item, dict):
            continue
        index_info = item.get("indexInfo")
        if not isinstance(index_info, dict):
            continue
        value = index_info.get("value")
        if isinstance(value, (int, float)):
            values.append(int(value))

    pollen_index = str(max(values) if values else 0)

    plant_info = today.get("plantInfo")
    if not isinstance(plant_info, list):
        plant_info = []

    species: list[str] = []
    for item in plant_info:
        if not isinstance(item, dict):
            continue
        if item.get("inSeason") is not True:
            continue
        display_name = item.get("displayName")
        if isinstance(display_name, str):
            cleaned = display_name.strip()
            if cleaned and cleaned not in species:
                species.append(cleaned)

    pollen_species = "/".join(species[:5]) + ("..." if len(species) > 5 else "")
    if not pollen_species:
        pollen_species = "unknown"

    return {
        "location": location_name,
        "pollen-index": pollen_index,
        "pollen-species": pollen_species,
    }


def main() -> None:
    api_key = load_api_key()
    input_payload = load_payload(INPUT_JSON_PATH)
    latitude, longitude = extract_coordinates(input_payload)

    pollen_payload = fetch_pollen_forecast(api_key, latitude, longitude)
    location_name = reverse_geocode_city(api_key, latitude, longitude)

    result = summarize_forecast(pollen_payload, location_name)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()