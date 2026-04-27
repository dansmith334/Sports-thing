"""Client for pulling pregame moneyline odds from The Odds API."""

from __future__ import annotations

from typing import Any

import requests


class OddsApiClient:
    BASE_URL = "https://api.the-odds-api.com/v4/sports"

    def __init__(self, api_key: str, regions: str) -> None:
        self.api_key = api_key
        self.regions = regions

    def get_pregame_moneyline_odds(self, sport_key: str) -> list[dict[str, Any]]:
        """Fetch h2h pregame moneyline odds for one sport."""
        url = f"{self.BASE_URL}/{sport_key}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": self.regions,
            "markets": "h2h",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }

        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            print(f"[ERROR] Odds API request failed for {sport_key}: {exc}")
            return []
