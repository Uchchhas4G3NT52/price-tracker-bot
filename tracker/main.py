"""
main.py - Orchestrates a single price-check run.

Usage:
    python -m tracker.main
"""
import os
import sys

from dotenv import load_dotenv

from tracker.database import get_latest_check, init_db, save_check
from tracker.notifier import send_telegram_message
from tracker.scraper import fetch_html, parse_product_page

load_dotenv()

DEFAULT_URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"


def run_check(url: str = None) -> None:
    url = url or os.environ.get("TARGET_URL") or DEFAULT_URL
    init_db()

    html = fetch_html(url)
    product = parse_product_page(html)

    previous = get_latest_check(product.title)

    save_check(
        title=product.title,
        price=product.price,
        in_stock=product.in_stock,
        stock_count=product.stock_count,
    )

    print(f"Checked '{product.title}': £{product.price:.2f}, in_stock={product.in_stock}")

    if previous is None:
        send_telegram_message(
            f"📍 Started tracking '{product.title}'\nPrice: £{product.price:.2f}"
        )
        return

    if product.price < previous.price:
        send_telegram_message(
            f"📉 Price drop for '{product.title}'!\n"
            f"£{previous.price:.2f} -> £{product.price:.2f}"
        )
    elif product.price > previous.price:
        send_telegram_message(
            f"📈 Price increase for '{product.title}'\n"
            f"£{previous.price:.2f} -> £{product.price:.2f}"
        )

    if not previous.in_stock and product.in_stock:
        send_telegram_message(f"✅ '{product.title}' is back in stock!")
    elif previous.in_stock and not product.in_stock:
        send_telegram_message(f"❌ '{product.title}' just went out of stock")


if __name__ == "__main__":
    try:
        run_check()
    except Exception as exc:  # top-level guard so scheduled runs fail loudly but gracefully
        print(f"Price check failed: {exc}", file=sys.stderr)
        sys.exit(1)
