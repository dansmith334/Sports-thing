"""Main loop for the sports arbitrage alert bot MVP."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from arbitrage import (
    build_opportunity_id,
    calculate_stake_split,
    detect_arbitrage,
    find_best_moneyline_prices,
)
from config import SUPPORTED_SPORTS, load_settings
from database import AlertDatabase
from odds_api import OddsApiClient
from telegram_alerts import TelegramAlerter


def format_alert_message(
    sport_name: str,
    event_name: str,
    start_time: str,
    best_prices: dict,
    implied_total: float,
    edge_percent: float,
    stake_split: dict,
) -> str:
    teams = list(best_prices.keys())
    team_a, team_b = teams[0], teams[1]

    return (
        "Possible arbitrage found\n\n"
        f"Sport: {sport_name}\n"
        f"Event: {event_name}\n"
        f"Start time: {start_time}\n"
        "Market: Moneyline\n\n"
        "Best prices:\n"
        f"- {team_a}: {best_prices[team_a]['american_odds']:+.0f}, {best_prices[team_a]['bookmaker']}\n"
        f"- {team_b}: {best_prices[team_b]['american_odds']:+.0f}, {best_prices[team_b]['bookmaker']}\n\n"
        f"Implied probability total: {implied_total:.4f}\n"
        f"Estimated edge: {edge_percent:.2f}%\n"
        "Suggested stake split:\n"
        f"- {team_a}: ${stake_split[team_a]:.2f}\n"
        f"- {team_b}: ${stake_split[team_b]:.2f}\n\n"
        "Warning: verify manually before betting. Odds can move, limits can apply, and markets can have different rules."
    )


def scan_once(
    client: OddsApiClient,
    db: AlertDatabase,
    alerter: TelegramAlerter,
    min_arb_percent: float,
    total_stake: float,
) -> None:
    found_any = False

    for sport_key, sport_name in SUPPORTED_SPORTS.items():
        print(f"[{datetime.now(timezone.utc).isoformat()}] Checking {sport_name}...")
        events = client.get_pregame_moneyline_odds(sport_key)

        for event in events:
            best_prices = find_best_moneyline_prices(event)
            is_arb, implied_total, edge_percent = detect_arbitrage(best_prices)

            if not is_arb or edge_percent <= min_arb_percent:
                continue

            if len(best_prices) != 2:
                # Keep MVP simple: only two-outcome events.
                continue

            event_id = event.get("id", "unknown")
            start_time = event.get("commence_time", "unknown")
            home_team = event.get("home_team", "Unknown")
            away_team = event.get("away_team", "Unknown")
            event_name = f"{away_team} @ {home_team}"

            opportunity_id = build_opportunity_id(
                sport_key=sport_key,
                event_id=event_id,
                start_time=start_time,
                best_prices=best_prices,
            )

            if db.was_sent(opportunity_id):
                continue

            stake_split, _, _ = calculate_stake_split(total_stake, best_prices)
            message = format_alert_message(
                sport_name,
                event_name,
                start_time,
                best_prices,
                implied_total,
                edge_percent,
                stake_split,
            )

            sent = alerter.send_message(message)
            if sent:
                db.save_alert(
                    opportunity_id=opportunity_id,
                    sport_key=sport_key,
                    event_id=event_id,
                    event_name=event_name,
                    start_time=start_time,
                    implied_total=implied_total,
                    edge_percent=edge_percent,
                )
                print(f"[ALERT] Sent arbitrage alert for {event_name} ({sport_name})")
                found_any = True

    if not found_any:
        print("No opportunities found.")


def main() -> None:
    settings = load_settings()
    client = OddsApiClient(settings.odds_api_key, settings.regions)
    db = AlertDatabase()
    alerter = TelegramAlerter(settings.telegram_bot_token, settings.telegram_chat_id)

    print("Sports arbitrage scanner started.")
    print(f"Refresh interval: {settings.refresh_seconds} seconds")

    while True:
        try:
            scan_once(
                client=client,
                db=db,
                alerter=alerter,
                min_arb_percent=settings.min_arb_percent,
                total_stake=settings.total_stake,
            )
        except Exception as exc:  # Keep process running in MVP mode.
            print(f"[ERROR] Unexpected scanner error: {exc}")

        time.sleep(settings.refresh_seconds)


if __name__ == "__main__":
    main()
