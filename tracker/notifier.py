"""
notifier.py - Sends alerts via Telegram when something noteworthy happens.

Setup (one-time):
1. Message @BotFather on Telegram, send /newbot, follow the prompts.
   You'll get a bot token that looks like "123456789:ABCdefGhIJKlmNoPQRsTuVwXyZ"
2. Start a chat with your new bot and send it any message.
3. Visit https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates in a browser
   to find your chat ID in the response JSON.
4. Put both values in your .env file (see .env.example).
"""
import os

import requests

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(message: str) -> bool:
    """
    Send a message via Telegram bot.

    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.
    Returns True if the message sent successfully, False otherwise (and
    never raises, since a failed notification shouldn't crash the whole run).
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram credentials not set; skipping notification.")
        return False

    url = TELEGRAM_API_URL.format(token=token)
    try:
        response = requests.post(
            url, data={"chat_id": chat_id, "text": message}, timeout=10
        )
    except requests.RequestException as exc:
        print(f"Failed to reach Telegram: {exc}")
        return False

    if response.status_code != 200:
        print(f"Telegram API returned an error: {response.text}")
        return False

    return True
