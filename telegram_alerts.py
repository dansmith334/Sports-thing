"""Telegram alert sender for arbitrage opportunities."""

from __future__ import annotations

import requests


class TelegramAlerter:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_message(self, message: str) -> bool:
        payload = {
            "chat_id": self.chat_id,
            "text": message,
        }
        try:
            response = requests.post(self.url, json=payload, timeout=15)
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            print(f"[ERROR] Failed to send Telegram message: {exc}")
            return False
