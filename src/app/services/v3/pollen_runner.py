import json
from typing import Any, TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

POLLEN_API_URL = "https://pollen.googleapis.com/v1/forecast:lookup"
GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DEFAULT_LANGUAGE_CODE = "ja"
DEFAULT_DAYS = 1

PollenResult = TypedDict(
    "PollenResult",
    {
        "location": str,
        "pollen-index": str,
        "pollen-species": str,
    },
)


class PollenRunner:
    def __init__(self, api_key: str, language_code: str = DEFAULT_LANGUAGE_CODE, days: int = DEFAULT_DAYS) -> None:
        if not api_key:
            raise ValueError("api_key is required.")
        if days < 1:
            raise ValueError("days must be >= 1.")

        self._api_key = api_key
        self._language_code = language_code
        self._days = days

    def run(self, payload: dict[str, Any]) -> PollenResult:
        latitude, longitude = self._extract_coordinates(payload)
        pollen_payload = self._fetch_pollen_forecast(latitude, longitude)
        location_name = self._reverse_geocode_city(latitude, longitude)
        return self._summarize_forecast(pollen_payload, location_name)

    def _extract_coordinates(self, payload: dict[str, Any]) -> tuple[float, float]:
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

    def _fetch_pollen_forecast(self, latitude: float, longitude: float) -> dict[str, Any]:
        params = {
            "location.latitude": str(latitude),
            "location.longitude": str(longitude),
            "days": str(self._days),
            "languageCode": self._language_code,
            "plantsDescription": "true",
            "key": self._api_key,
        }
        return self._fetch_json(POLLEN_API_URL, params)

    def _reverse_geocode_city(self, latitude: float, longitude: float) -> str:
        params = {
            "latlng": f"{latitude},{longitude}",
            "language": self._language_code,
            "key": self._api_key,
            "result_type": (
                "locality|administrative_area_level_2|"
                "administrative_area_level_3|administrative_area_level_1"
            ),
        }
        payload = self._fetch_json(GEOCODING_API_URL, params)

        if payload.get("status") != "OK":
            return "unknown"

        results = payload.get("results")
        if not isinstance(results, list) or not results:
            return "unknown"

        priority_types = [
            "locality",
            "administrative_area_level_2",
            "administrative_area_level_3",
        ]

        for target_type in priority_types:
            for result in results:
                if not isinstance(result, dict):
                    continue
                address_components = result.get("address_components")
                if not isinstance(address_components, list):
                    continue

                for comp in address_components:
                    if not isinstance(comp, dict):
                        continue
                    comp_types = comp.get("types")
                    if isinstance(comp_types, list) and target_type in comp_types:
                        long_name = comp.get("long_name")
                        if isinstance(long_name, str) and long_name.strip():
                            return long_name.strip()

        for result in results:
            if not isinstance(result, dict):
                continue
            address_components = result.get("address_components")
            if not isinstance(address_components, list):
                continue

            for comp in address_components:
                if not isinstance(comp, dict):
                    continue
                comp_types = comp.get("types")
                if isinstance(comp_types, list) and "administrative_area_level_1" in comp_types:
                    long_name = comp.get("long_name")
                    if isinstance(long_name, str) and long_name.strip():
                        return long_name.strip()

        formatted_address = results[0].get("formatted_address")
        if isinstance(formatted_address, str) and formatted_address.strip():
            return formatted_address.strip()
        return "unknown"

    def _summarize_forecast(self, pollen_payload: dict[str, Any], location_name: str) -> PollenResult:
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

    def _fetch_json(self, url: str, params: dict[str, str]) -> dict[str, Any]:
        request = Request(f"{url}?{urlencode(params)}", method="GET")
        try:
            with urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"API request failed: {error.code} {body}") from error
        except URLError as error:
            raise RuntimeError(f"API request failed: {error.reason}") from error
