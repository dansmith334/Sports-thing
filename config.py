"""Configuration loading for the sports arbitrage scanner."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


SUPPORTED_SPORTS = {
    "basketball_nba": "NBA",
    "americanfootball_nfl": "NFL",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
}


@dataclass
class Settings:
    odds_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    refresh_seconds: int
    min_arb_percent: float
    total_stake: float
    regions: str


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    """Load settings from .env and return a typed settings object."""
    load_dotenv()

    return Settings(
        odds_api_key=_required_env("ODDS_API_KEY"),
        telegram_bot_token=_required_env("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=_required_env("TELEGRAM_CHAT_ID"),
        refresh_seconds=int(os.getenv("REFRESH_SECONDS", "60")),
        min_arb_percent=float(os.getenv("MIN_ARB_PERCENT", "0.5")),
        total_stake=float(os.getenv("TOTAL_STAKE", "100")),
        regions=os.getenv("REGIONS", "us"),
    )
