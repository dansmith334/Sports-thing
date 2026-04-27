"""Arbitrage calculations and helpers."""

from __future__ import annotations

import hashlib
from typing import Any


def american_to_decimal(american_odds: float) -> float:
    """Convert American odds to decimal odds."""
    if american_odds == 0:
        raise ValueError("American odds cannot be zero")

    if american_odds > 0:
        return 1 + (american_odds / 100)

    return 1 + (100 / abs(american_odds))


def implied_probability(decimal_odds: float) -> float:
    """Convert decimal odds to implied probability."""
    if decimal_odds <= 1:
        raise ValueError("Decimal odds must be greater than 1")
    return 1 / decimal_odds


def find_best_moneyline_prices(event: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Find the best available moneyline price for each team in an event."""
    best_prices: dict[str, dict[str, Any]] = {}

    for bookmaker in event.get("bookmakers", []):
        bookmaker_name = bookmaker.get("title", "Unknown")

        for market in bookmaker.get("markets", []):
            if market.get("key") != "h2h":
                continue

            for outcome in market.get("outcomes", []):
                team_name = outcome.get("name")
                american = outcome.get("price")
                if team_name is None or american is None:
                    continue

                decimal = american_to_decimal(float(american))
                existing = best_prices.get(team_name)

                if not existing or decimal > existing["decimal_odds"]:
                    best_prices[team_name] = {
                        "american_odds": float(american),
                        "decimal_odds": decimal,
                        "bookmaker": bookmaker_name,
                    }

    return best_prices


def detect_arbitrage(best_prices: dict[str, dict[str, Any]]) -> tuple[bool, float, float]:
    """Return (is_arb, implied_total, edge_percent)."""
    if len(best_prices) < 2:
        return False, 0.0, 0.0

    implied_total = sum(
        implied_probability(team_data["decimal_odds"]) for team_data in best_prices.values()
    )
    edge_percent = (1 - implied_total) * 100
    return implied_total < 1.0, implied_total, edge_percent


def calculate_stake_split(
    total_stake: float, best_prices: dict[str, dict[str, Any]]
) -> tuple[dict[str, float], float, float]:
    """Return per-team stakes, expected payout, and expected profit."""
    inverse_sum = sum(1 / data["decimal_odds"] for data in best_prices.values())
    if inverse_sum <= 0:
        raise ValueError("Invalid odds data for stake split")

    stakes: dict[str, float] = {}
    for team, data in best_prices.items():
        weight = (1 / data["decimal_odds"]) / inverse_sum
        stakes[team] = round(total_stake * weight, 2)

    # Recompute payout using unrounded proportions for cleaner estimate.
    expected_payout = round(total_stake / inverse_sum, 2)
    expected_profit = round(expected_payout - total_stake, 2)
    return stakes, expected_payout, expected_profit


def build_opportunity_id(
    sport_key: str,
    event_id: str,
    start_time: str,
    best_prices: dict[str, dict[str, Any]],
) -> str:
    """Create a deterministic ID so duplicate alerts are not resent."""
    sorted_teams = sorted(
        (
            team,
            details["american_odds"],
            details["bookmaker"],
        )
        for team, details in best_prices.items()
    )
    raw = f"{sport_key}|{event_id}|{start_time}|{sorted_teams}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
