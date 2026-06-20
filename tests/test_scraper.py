"""
test_scraper.py - Tests for scraper.py using a saved HTML fixture
instead of hitting the live website. This keeps tests fast and
reliable even if the real site is down or changes its layout.
"""
from pathlib import Path

import pytest

from tracker.scraper import _parse_price, _parse_stock_count, parse_product_page

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_html() -> str:
    return (FIXTURES_DIR / "sample_page.html").read_text(encoding="utf-8")


def test_parse_product_page_extracts_title(sample_html):
    product = parse_product_page(sample_html)
    assert product.title == "A Light in the Attic"


def test_parse_product_page_extracts_price(sample_html):
    product = parse_product_page(sample_html)
    assert product.price == 51.77


def test_parse_product_page_extracts_stock_status(sample_html):
    product = parse_product_page(sample_html)
    assert product.in_stock is True
    assert product.stock_count == 22


def test_parse_product_page_missing_title_raises():
    with pytest.raises(ValueError):
        parse_product_page("<html><body>No title here</body></html>")


def test_parse_product_page_missing_price_raises():
    html = "<html><body><h1>Some Book</h1></body></html>"
    with pytest.raises(ValueError):
        parse_product_page(html)


@pytest.mark.parametrize(
    "raw_price,expected",
    [
        ("£51.77", 51.77),
        ("$10.00", 10.00),
        ("19.99", 19.99),
    ],
)
def test_parse_price_handles_currency_symbols(raw_price, expected):
    assert _parse_price(raw_price) == expected


def test_parse_price_raises_on_garbage_input():
    with pytest.raises(ValueError):
        _parse_price("not a price")


def test_parse_stock_count_extracts_number():
    assert _parse_stock_count("In stock (22 available)") == 22


def test_parse_stock_count_returns_none_when_absent():
    assert _parse_stock_count("Out of stock") is None
