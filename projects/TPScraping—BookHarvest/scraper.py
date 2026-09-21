import csv
import json
import re
import time
from   pathlib      import Path
from   urllib.parse import urljoin
import requests
from   bs4          import BeautifulSoup
from   rich.progress import (
                                Progress,
                                SpinnerColumn,
                                BarColumn,
                                TextColumn,
                                TimeElapsedColumn,
)                                                  # Pour des impressions plus jolies



BASE_URL = "https://books.toscrape.com/"
FIRST_PAGE_URL = urljoin(BASE_URL, "index.html")

STAR_RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


# Télécharger / parser
def fetch_html(url, session, timeout=10, retries=3):
    """
    Télécharger le HTML d'une URL et le retourne sous forme de texte.
    Réessayer jusqu'à ``retries`` fois en cas d'erreur réseau.
    """
    last_exc = None
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(1)                            # 1 seconde
    raise last_exc


def parse_html(html):
    """Transformer une chaîne HTML en objet BeautifulSoup."""
    return BeautifulSoup(html, "html.parser")


# Page listing
def get_listing_title(book):
    return book.find("h3").find("a")["title"]


def get_price(book):
    text = book.find(class_="price_color").get_text(strip=True)
    match = re.search(r"[\d.]+", text)
    return float(match.group())


def get_star_rating(book):
    """La note est encodée dans une classe CSS, ex. 'star-rating Three'."""
    tag = book.find(class_="star-rating")
    for css_class in tag.get("class", []):
        if css_class in STAR_RATINGS:
            return STAR_RATINGS[css_class]
    return None


def get_stock_status(book):
    tag = book.find(class_="instock")
    if tag is None:
        return False
    return "In stock" in tag.get_text()


def get_thumbnail_url(book):
    return book.find("img")["src"]


def get_listing_relative_url(book):
    """URL relative vers la page de détail du livre."""
    return book.find("h3").find("a")["href"]


# Page détail
def _find_table_value(soup, label):
    for row in soup.select("table tr"):
        th, td = row.find("th"), row.find("td")
        if th and td and th.get_text(strip=True) == label:
            return td.get_text(strip=True)
    return None


def get_upc(soup):
    """C'est une ligne d'un tableau HTML."""
    return _find_table_value(soup, "UPC")


def get_description(soup):
    heading = soup.find("div", id="product_description")
    if heading is None:
        return ""
    paragraph = heading.find_next_sibling("p")
    return paragraph.get_text(strip=True) if paragraph else ""


def get_number_available(soup):
    """Le texte ressemble à 'In stock (22 available)'."""
    value = _find_table_value(soup, "Availability")
    if not value:
        return 0
    match = re.search(r"\((\d+)\s+available\)", value)
    return int(match.group(1)) if match else 0


def get_detail_image_url(soup):
    gallery = soup.find(id="product_gallery")
    return gallery.find("img")["src"]


# Pagination et orchestration
def get_book_links_from_page(soup):
    """Retourne la liste des blocs <article class="product_pod"> d'une page."""
    return soup.find_all("article", class_="product_pod")


def _extract_page_number(page_url):
    """Extrait le numéro de page à partir de l'URL, pour l'affichage."""
    match = re.search(r"page-(\d+)\.html", page_url)
    return int(match.group(1)) if match else 1 # 1 par défaut


def iter_catalogue_pages(session, delay=0.5):
    """
    Générateur parcourant toutes les pages du catalogue.
    S'arrêter dès qu'aucun élément <li class="next"> n'est trouvé : aucune
    valeur codée en dur, la fin du catalogue est détectée dynamiquement.
    """
    url = FIRST_PAGE_URL
    while url:
        html = fetch_html(url, session)
        soup = parse_html(html)
        yield url, soup

        next_li = soup.find("li", class_="next")
        if next_li is None:
            break
        next_href = next_li.find("a")["href"]
        url       = urljoin(url, next_href)
        time.sleep(delay)  # politesse  d'une demi-seconde envers le serveur


class ColoredTimeElapsedColumn(TimeElapsedColumn):
    """TimeElapsedColumn avec une couleur imposée plutôt que le thème par défaut."""
    def render(self, task):
        text = super().render(task)
        text.stylize("bold sky_blue1")
        return text


def scrape_book(book_tag, page_url, session):
    """Récupère toutes les infos d'un livre (listing + détail) sous forme de dict."""
    detail_relative = get_listing_relative_url(book_tag)
    detail_url      = urljoin(page_url, detail_relative)

    detail_html = fetch_html(detail_url, session)
    detail_soup = parse_html(detail_html)

    thumbnail_url = urljoin(page_url, get_thumbnail_url(book_tag))
    image_url     = urljoin(detail_url, get_detail_image_url(detail_soup))

    return {
        "title":            get_listing_title(book_tag),
        "price":            get_price(book_tag),
        "star_rating":      get_star_rating(book_tag),
        "in_stock":         get_stock_status(book_tag),
        "thumbnail_url":    thumbnail_url,
        "detail_url":       detail_url,
        "upc":              get_upc(detail_soup),
        "description":      get_description(detail_soup),
        "number_available": get_number_available(detail_soup),
        "image_url":        image_url,
    }


def scrape_all_books(delay=0.5, show_progress=True):
    """Parcourt tout le catalogue et retourne la liste de tous les livres."""
    books = []
    with requests.Session() as session:
        with Progress(
            SpinnerColumn(style="bold green1"),
            TextColumn("[bold green]Extraction depuis[/bold green] [dim]books.toscrape.com[/dim]"),
            BarColumn(bar_width=15, style="green4", pulse_style="bright_green on green4"),
            TextColumn(" [bold bright_white]{task.completed}[/bold bright_white] livre·s"),
            TextColumn("• [bold bright_white]{task.fields[page]}[/bold bright_white] page·s "),
            TextColumn("• [italic yellow]{task.fields[titre]}[/italic yellow] •"),
            ColoredTimeElapsedColumn(),
            disable=not show_progress,
        ) as progress:
            task = progress.add_task("scraping", total=None, page=1, titre="—")
            for page_url, soup in iter_catalogue_pages(session, delay=delay):
                page_number = _extract_page_number(page_url)
                for book_tag in get_book_links_from_page(soup):
                    title = get_listing_title(book_tag)
                    record = scrape_book(book_tag, page_url, session)
                    books.append(record)
                    progress.update(task, advance=1, page=page_number, titre=title[:30])
    return books


# Sortie
def save_to_csv(records, path="books.csv"):
    """Écrit la liste de dictionnaires dans un fichier CSV."""
    if not records:
        Path(path).write_text("", encoding="utf-8")
        return
    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def save_to_json(records, path="books.json"):
    """Écrit la liste de dictionnaires dans un fichier JSON (bonus)."""
    Path(path).write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def bold_green(text):
    """Retourne le texte en gras et en vert dans un terminal ANSI."""
    return f"\033[1;32m{text}\033[0m"


def italic_soft_yellow(text):
    """Retourne le texte en italique et en jaune doux (256 couleurs) dans un terminal ANSI."""
    return f"\033[3;38;5;229m{text}\033[0m"


if __name__ == "__main__":
    books = scrape_all_books()
    save_to_csv(books)
    save_to_json(books)
    # print(f"✔️ \033[1m{len(books)}\033[0m \033[1mlivres\033[0m sont sauvegardés dans books.csv et books.json")
    print(
        f"{bold_green('✔ ')}{bold_green(len(books))} {bold_green('livres')} "
        f"dans {italic_soft_yellow('books.csv')} et {italic_soft_yellow('books.json')}"
    )