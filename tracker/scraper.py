"""
scraper.py - Fetches and parses product info from a tracked webpage.

Target site: books.toscrape.com - a sandbox site built specifically for
scraping practice, so it's safe to use for a portfolio project (no real
store's terms of service to worry about, and the HTML structure is stable).
"""
from dataclasses import dataclass
from typing import Optional
import re

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; PriceTrackerBot/1.0)"


@dataclass
class ProductInfo:
    title: str
    price: float
    in_stock: bool
    stock_count: Optional[int]


def fetch_html(url: str, timeout: int = 10) -> str:
    """Download the raw HTML for a given URL."""
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_product_page(html: str) -> ProductInfo:
    """
    Parse a books.toscrape.com-style product page and extract
    title, price, and stock info.

    Raises ValueError if expected elements are missing, so callers know
    the page structure changed rather than silently returning bad data.
    """
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1")
    if not title_tag:
        raise ValueError("Could not find product title on page")
    title = title_tag.get_text(strip=True)

    price_tag = soup.find("p", class_="price_color")
    if not price_tag:
        raise ValueError("Could not find price on page")
    price = _parse_price(price_tag.get_text(strip=True))

    availability_tag = soup.find("p", class_="instock availability")
    if not availability_tag:
        raise ValueError("Could not find availability info on page")
    availability_text = availability_tag.get_text(strip=True)
    in_stock = "in stock" in availability_text.lower()
    stock_count = _parse_stock_count(availability_text)

    return ProductInfo(title=title, price=price, in_stock=in_stock, stock_count=stock_count)


def _parse_price(raw_price: str) -> float:
    """Strip currency symbols and convert to float, e.g. '£51.77' -> 51.77"""
    match = re.search(r"[\d.]+", raw_price)
    if not match:
        raise ValueError(f"Could not parse price from '{raw_price}'")
    return float(match.group())


def _parse_stock_count(text: str) -> Optional[int]:
    """Extract a number like '(22 available)' -> 22, or None if absent."""
    match = re.search(r"\((\d+)\s+available\)", text)
    return int(match.group(1)) if match else None
