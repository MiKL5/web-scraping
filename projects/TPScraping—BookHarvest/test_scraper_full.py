from __future__ import annotations

import csv
import json
import socket
import time
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urljoin

import pytest
import requests
from bs4 import BeautifulSoup

import scraper


# HTML factice
LISTING_HTML = """
<article class="product_pod">
    <div class="image_container">
        <a href="catalogue/a-light-in-the-attic_1000/index.html">
            <img src="media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg" alt="A Light in the Attic">
        </a>
    </div>
    <p class="star-rating Three"></p>
    <h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the Attic</a></h3>
    <div class="product_price">
        <p class="price_color">£51.77</p>
        <p class="instock availability"><i class="icon-ok"></i> In stock</p>
    </div>
</article>
"""

DETAIL_HTML = """
<html><body>
<div id="product_gallery"><div class="thumbnail">
<img src="../../../../media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg"></div></div>
<div id="product_description" class="sub-header"><h2>Product Description</h2></div>
<p>It's hard to imagine a world without A Light in the Attic.</p>
<table class="table table-striped">
<tr><th>UPC</th><td>a897fe39b1053632</td></tr>
<tr><th>Availability</th><td>In stock (22 available)</td></tr>
</table>
</body></html>
"""

DETAIL_HTML_NO_COUNT = """
<html><body><table><tr><th>UPC</th><td>a897fe39b1053632</td></tr>
<tr><th>Availability</th><td>In stock</td></tr></table></body></html>
"""

DETAIL_HTML_NO_DESCRIPTION = """
<html><body><table><tr><th>UPC</th><td>a897fe39b1053632</td></tr>
<tr><th>Availability</th><td>In stock (22 available)</td></tr></table></body></html>
"""

DETAIL_HTML_NO_UPC = """
<html><body><table><tr><th>Price</th><td>£51.77</td></tr></table></body></html>
"""


@pytest.fixture
def listing_soup():
    return BeautifulSoup(LISTING_HTML, "html.parser")


@pytest.fixture
def detail_soup():
    return BeautifulSoup(DETAIL_HTML, "html.parser")


# 1. fetch_html — réseau simulé, aucun appel réel
def _has_internet(host="books.toscrape.com", port=443, timeout=3):
    """Vérifie la disponibilité du réseau avant un test d'intégration réel."""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False


class FakeResponse:
    def __init__(self, text, ok=True):
        self.text = text
        self._ok = ok

    def raise_for_status(self):
        if not self._ok:
            raise requests.exceptions.HTTPError("404 simulé")


class FlakySession:
    """Session factice qui échoue N fois avant de réussir (ou jamais)."""
    def __init__(self, fail_times, html="OK"):
        self.calls = 0
        self.fail_times = fail_times
        self.html = html

    def get(self, url, timeout=10):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise requests.exceptions.ConnectionError("panne réseau simulée")
        return FakeResponse(self.html)


def test_fetch_html_success_first_try(monkeypatch):
    monkeypatch.setattr(scraper.time, "sleep", lambda s: None)
    session = FlakySession(fail_times=0, html="<p>ok</p>")
    assert scraper.fetch_html("http://x", session) == "<p>ok</p>"
    assert session.calls == 1


def test_fetch_html_succeeds_after_retries(monkeypatch):
    monkeypatch.setattr(scraper.time, "sleep", lambda s: None)
    session = FlakySession(fail_times=2, html="<p>ok</p>")
    result = scraper.fetch_html("http://x", session, retries=3)
    assert result == "<p>ok</p>"
    assert session.calls == 3


def test_fetch_html_raises_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr(scraper.time, "sleep", lambda s: None)
    session = FlakySession(fail_times=99, html="<p>ok</p>")
    with pytest.raises(requests.exceptions.ConnectionError):
        scraper.fetch_html("http://x", session, retries=3)
    assert session.calls == 3


def test_fetch_html_raises_http_error_on_bad_status(monkeypatch):
    monkeypatch.setattr(scraper.time, "sleep", lambda s: None)

    class BadStatusSession:
        def get(self, url, timeout=10):
            return FakeResponse("erreur", ok=False)

    with pytest.raises(requests.exceptions.HTTPError):
        scraper.fetch_html("http://x", BadStatusSession(), retries=1)


# 2. Parsing et extraction — page listing
def test_parse_html_returns_beautifulsoup():
    soup = scraper.parse_html("<p>hello</p>")
    assert isinstance(soup, BeautifulSoup)
    assert soup.select_one("p").get_text() == "hello"


def test_get_listing_title(listing_soup):
    assert scraper.get_listing_title(listing_soup) == "A Light in the Attic"


def test_get_listing_relative_url(listing_soup):
    assert scraper.get_listing_relative_url(listing_soup) == "catalogue/a-light-in-the-attic_1000/index.html"


def test_get_price(listing_soup):
    assert scraper.get_price(listing_soup) == pytest.approx(51.77)


def test_get_star_rating():
    for word, expected in scraper.STAR_RATINGS.items():
        soup = BeautifulSoup(f'<p class="star-rating {word}"></p>', "html.parser")
        assert scraper.get_star_rating(soup) == expected


def test_get_stock_status():
    in_stock = BeautifulSoup('<p class="instock availability">In stock</p>', "html.parser")
    out_of_stock = BeautifulSoup('<p class="instock availability">Out of stock</p>', "html.parser")
    assert scraper.get_stock_status(in_stock) is True
    assert scraper.get_stock_status(out_of_stock) is False


def test_get_thumbnail_url(listing_soup):
    assert scraper.get_thumbnail_url(listing_soup) == "media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg"


# 3. Extraction — page détail (+ cas limites)
def test_get_upc(detail_soup):
    assert scraper.get_upc(detail_soup) == "a897fe39b1053632"


def test_get_upc_returns_none_when_absent():
    soup = BeautifulSoup(DETAIL_HTML_NO_UPC, "html.parser")
    assert scraper.get_upc(soup) is None


def test_get_number_available(detail_soup):
    assert scraper.get_number_available(detail_soup) == 22


def test_get_number_available_returns_zero_when_missing():
    soup = BeautifulSoup(DETAIL_HTML_NO_COUNT, "html.parser")
    assert scraper.get_number_available(soup) == 0


def test_get_description(detail_soup):
    assert scraper.get_description(detail_soup).startswith(
        "It's hard to imagine a world without A Light in the Attic."
    )


def test_get_description_returns_empty_when_missing():
    soup = BeautifulSoup(DETAIL_HTML_NO_DESCRIPTION, "html.parser")
    assert scraper.get_description(soup) == ""


def test_get_detail_image_url(detail_soup):
    assert scraper.get_detail_image_url(detail_soup) == "../../../../media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg"


# 4. Listing, pagination, numérotation de page
def test_get_book_links_from_page_returns_all_articles():
    page_html = f"<html><body>{LISTING_HTML}{LISTING_HTML}</body></html>"
    soup = BeautifulSoup(page_html, "html.parser")
    assert len(scraper.get_book_links_from_page(soup)) == 2


def test_extract_page_number_from_url():
    assert scraper._extract_page_number("https://x/catalogue/page-7.html") == 7


def test_extract_page_number_defaults_to_one_without_match():
    assert scraper._extract_page_number("https://x/index.html") == 1


def test_iter_catalogue_pages_follows_next_then_stops(monkeypatch):
    page1_url = scraper.FIRST_PAGE_URL
    page2_url = urljoin(page1_url, "page-2.html")
    page1_html = f'<html><body>{LISTING_HTML}<li class="next"><a href="page-2.html">next</a></li></body></html>'
    page2_html = f"<html><body>{LISTING_HTML}</body></html>"
    pages = {page1_url: page1_html, page2_url: page2_html}

    def fake_fetch_html(url, session, timeout=10, retries=3):
        return pages[url]

    monkeypatch.setattr(scraper, "fetch_html", fake_fetch_html)
    monkeypatch.setattr(scraper.time, "sleep", lambda seconds: None)

    results = list(scraper.iter_catalogue_pages(session=None, delay=0))
    assert [url for url, _ in results] == [page1_url, page2_url]


# 5. scrape_book — assemblage listing + détail, URLs absolues
def test_scrape_book_assembles_full_record(monkeypatch, listing_soup):
    monkeypatch.setattr(scraper, "fetch_html", lambda url, session, timeout=10, retries=3: DETAIL_HTML)
    page_url = "https://books.toscrape.com/catalogue/page-1.html"

    record = scraper.scrape_book(listing_soup, page_url, session=None)

    assert record["title"] == "A Light in the Attic"
    assert record["price"] == pytest.approx(51.77)
    assert record["star_rating"] == 3
    assert record["in_stock"] is True
    assert record["upc"] == "a897fe39b1053632"
    assert record["number_available"] == 22
    assert record["thumbnail_url"].startswith("https://books.toscrape.com/")
    assert record["detail_url"].startswith("https://books.toscrape.com/")
    assert record["image_url"].startswith("https://books.toscrape.com/")


# 6. scrape_all_books — orchestration complète
def test_scrape_all_books_aggregates_every_page(monkeypatch):
    page1_soup = BeautifulSoup(f"<html><body>{LISTING_HTML}</body></html>", "html.parser")
    page2_soup = BeautifulSoup(f"<html><body>{LISTING_HTML}{LISTING_HTML}</body></html>", "html.parser")
    fake_pages = [("https://x/page-1.html", page1_soup), ("https://x/page-2.html", page2_soup)]

    monkeypatch.setattr(scraper, "iter_catalogue_pages", lambda session, delay=0.5: iter(fake_pages))
    monkeypatch.setattr(scraper, "fetch_html", lambda url, session, timeout=10, retries=3: DETAIL_HTML)

    books = scraper.scrape_all_books(delay=0, show_progress=False)

    assert len(books) == 3
    assert all(b["title"] == "A Light in the Attic" for b in books)


def test_scrape_all_books_with_real_network_and_delay():
    """
    Test d'intégration : exécute scrape_all_books() contre le site réel,
    avec délai réellement actif, limité aux 2 premières pages de catalogue
    (40 livres) pour rester rapide et poli envers le serveur.
    """
    if not _has_internet():
        pytest.skip("Pas d'accès réseau disponible pour ce test d'intégration")

    original_iter = scraper.iter_catalogue_pages

    def limited_iter_catalogue_pages(session, delay=0.5):
        gen = original_iter(session, delay=delay)
        for _ in range(2):
            try:
                yield next(gen)
            except StopIteration:
                return

    scraper.iter_catalogue_pages = limited_iter_catalogue_pages
    start = time.time()
    try:
        books = scraper.scrape_all_books(delay=0.3, show_progress=False)
    finally:
        scraper.iter_catalogue_pages = original_iter
    elapsed = time.time() - start

    assert len(books) == 40
    assert elapsed >= 0.3  # preuve que le délai réel s'est bien appliqué au moins une fois

    for book in books:
        assert book["title"]
        assert book["price"] > 0
        assert 1 <= book["star_rating"] <= 5
        assert book["detail_url"].startswith("https://books.toscrape.com/")
        assert book["thumbnail_url"].startswith("https://books.toscrape.com/")
        assert book["image_url"].startswith("https://books.toscrape.com/")


# 7. Sortie : CSV et JSON

def test_save_to_csv_writes_expected_content(tmp_path):
    records = [{"title": "Book A", "price": 10.0}, {"title": "Book B", "price": 20.0}]
    csv_path = tmp_path / "out.csv"
    scraper.save_to_csv(records, path=str(csv_path))
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows == [{"title": "Book A", "price": "10.0"}, {"title": "Book B", "price": "20.0"}]


def test_save_to_csv_handles_empty_records(tmp_path):
    csv_path = tmp_path / "empty.csv"
    scraper.save_to_csv([], path=str(csv_path))
    assert csv_path.exists()
    assert csv_path.read_text(encoding="utf-8") == ""


def test_save_to_json_round_trips_data(tmp_path):
    records = [{"title": "Book A", "price": 10.0}, {"title": "Book B", "price": 20.0}]
    json_path = tmp_path / "out.json"
    scraper.save_to_json(records, path=str(json_path))
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded == records


# 8. Utilitaires d'affichage ANSI et rich
def test_bold_green_wraps_text_in_ansi_codes():
    assert scraper.bold_green("X") == "\033[1;32mX\033[0m"


def test_italic_soft_yellow_wraps_text_in_ansi_codes():
    assert scraper.italic_soft_yellow("X") == "\033[3;38;5;229mX\033[0m"


def test_colored_time_elapsed_column_applies_style():
    column = scraper.ColoredTimeElapsedColumn()
    fake_task = SimpleNamespace(finished=False, finished_time=None, elapsed=5.0)
    text = column.render(fake_task)
    assert "0:00:05" in text.plain
    assert any(span.style == "bold sky_blue1" for span in text.spans)