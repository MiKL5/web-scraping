import re
from   urllib.parse import urljoin
import pytest
from   bs4          import BeautifulSoup
import scraper

LISTING_HTML = """
<article class="product_pod">
    <div class="image_container">
        <a href="catalogue/a-light-in-the-attic_1000/index.html">
            <img src="media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg" alt="A Light in the Attic" class="thumbnail">
        </a>
    </div>
    <p class="star-rating Three">
        <i class="icon-star"></i><i class="icon-star"></i><i class="icon-star"></i>
    </p>
    <h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the Attic</a></h3>
    <div class="product_price">
        <p class="price_color">£51.77</p>
        <p class="instock availability">
            <i class="icon-ok"></i> In stock
        </p>
    </div>
</article>
"""

DETAIL_HTML = """
<html><body>
<div id="product_gallery">
    <div class="thumbnail">
        <img src="../../../../media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg" alt="A Light in the Attic">
    </div>
</div>
<div id="product_description" class="sub-header"><h2>Product Description</h2></div>
<p>It's hard to imagine a world without A Light in the Attic.</p>
<table class="table table-striped">
<tr><th>UPC</th><td>a897fe39b1053632</td></tr>
<tr><th>Product Type</th><td>Books</td></tr>
<tr><th>Price (excl. tax)</th><td>£51.77</td></tr>
<tr><th>Availability</th><td>In stock (22 available)</td></tr>
<tr><th>Number of reviews</th><td>0</td></tr>
</table>
</body></html>
"""

DETAIL_HTML_NO_COUNT = """
<html><body>
<table class="table table-striped">
<tr><th>UPC</th><td>a897fe39b1053632</td></tr>
<tr><th>Availability</th><td>In stock</td></tr>
</table>
</body></html>
"""

DETAIL_HTML_NO_DESCRIPTION = """
<html><body>
<table class="table table-striped">
<tr><th>UPC</th><td>a897fe39b1053632</td></tr>
<tr><th>Availability</th><td>In stock (22 available)</td></tr>
</table>
</body></html>
"""


@pytest.fixture
def listing_soup():
    return BeautifulSoup(LISTING_HTML, "html.parser")


@pytest.fixture
def detail_soup():
    return BeautifulSoup(DETAIL_HTML, "html.parser")


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


def test_get_upc(detail_soup):
    assert scraper.get_upc(detail_soup) == "a897fe39b1053632"


def test_get_number_available(detail_soup):
    assert scraper.get_number_available(detail_soup) == 22


def test_get_description(detail_soup):
    assert scraper.get_description(detail_soup).startswith("It's hard to imagine a world without A Light in the Attic.")


def test_get_detail_image_url(detail_soup):
    assert scraper.get_detail_image_url(detail_soup) == "../../../../media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg"


def test_get_number_available_returns_zero_when_missing():
    soup = BeautifulSoup(DETAIL_HTML_NO_COUNT, "html.parser")
    assert scraper.get_number_available(soup) == 0


def test_get_description_returns_empty_when_missing():
    soup = BeautifulSoup(DETAIL_HTML_NO_DESCRIPTION, "html.parser")
    assert scraper.get_description(soup) == ""


def test_get_book_links_from_page_returns_all_articles():
    page_html = f"<html><body>{LISTING_HTML}{LISTING_HTML}</body></html>"
    soup = BeautifulSoup(page_html, "html.parser")
    assert len(scraper.get_book_links_from_page(soup)) == 2


def test_iter_catalogue_pages_follows_next_then_stops(monkeypatch):
    page1_url = scraper.FIRST_PAGE_URL
    page2_url = urljoin(page1_url, "page-2.html")
    page1_html = f"<html><body>{LISTING_HTML}<li class=\'next\'><a href=\'page-2.html\'>next</a></li></body></html>"
    page2_html = f"<html><body>{LISTING_HTML}</body></html>"
    pages = {page1_url: page1_html, page2_url: page2_html}

    def fake_fetch_html(url, session, timeout=10, retries=3):
        return pages[url]

    monkeypatch.setattr(scraper, "fetch_html", fake_fetch_html)
    monkeypatch.setattr(scraper.time, "sleep", lambda seconds: None)

    results = list(scraper.iter_catalogue_pages(session=None, delay=0))
    assert [url for url, _ in results] == [page1_url, page2_url]


def test_save_to_csv_writes_expected_content(tmp_path):
    records = [{"title": "Book A", "price": 10.0}, {"title": "Book B", "price": 20.0}]
    csv_path = tmp_path / "out.csv"
    scraper.save_to_csv(records, path=str(csv_path))
    import csv as csv_mod
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv_mod.DictReader(f))
    assert rows == [{"title": "Book A", "price": "10.0"}, {"title": "Book B", "price": "20.0"}]
