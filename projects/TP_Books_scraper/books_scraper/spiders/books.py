import scrapy
from books_scraper.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        # Parse une page du catalogue
        book_nodes = response.xpath('//article[@class="product_pod"]')

        for book in book_nodes:
            title = book.xpath('.//h3/a/@title').get()

            raw_price = book.xpath('.//p[@class="price_color"]/text()').get()

            raw_rating_class = book.xpath(
                './/p[contains(@class, "star-rating")]/@class'
            ).get()

            raw_stock_parts = book.xpath(
                './/p[contains(@class, "instock")]/text()'
            ).getall()
            raw_stock_text = " ".join(raw_stock_parts)

            raw_thumbnail = book.xpath('.//img/@src').get()
            thumbnail_url = response.urljoin(raw_thumbnail)

            detail_href = book.xpath('.//h3/a/@href').get()

            catalogue_data = {
                "title": title,
                "price": raw_price,
                "star_rating": raw_rating_class,
                "in_stock": raw_stock_text,
                "thumbnail_url": thumbnail_url,
            }

            yield response.follow(
                detail_href,
                callback=self.parse_detail,
                cb_kwargs={"catalogue_data": catalogue_data},
            )

        next_href = response.xpath('//li[@class="next"]/a/@href').get()
        if next_href is not None:
            yield response.follow(next_href, callback=self.parse)

    def parse_detail(self, response, catalogue_data):
        """Parse la page de détail et fusionne les données brutes du catalogue
        avec celles extraites de la page de détail dans un BookItem."""
        item = BookItem()
        item["title"] = catalogue_data["title"]
        item["price"] = catalogue_data["price"]
        item["star_rating"] = catalogue_data["star_rating"]
        item["in_stock"] = catalogue_data["in_stock"]
        item["thumbnail_url"] = catalogue_data["thumbnail_url"]
        item["detail_url"] = response.url

        item["upc"] = response.xpath(
            '//table[@class="table table-striped"]'
            '//th[text()="UPC"]/following-sibling::td/text()'
        ).get()

        raw_description_parts = response.xpath(
            '//div[@id="product_description"]/following-sibling::p/text()'
        ).getall()
        item["description"] = " ".join(raw_description_parts) if raw_description_parts else None

        item["number_available"] = response.xpath(
            '//table[@class="table table-striped"]'
            '//th[text()="Availability"]/following-sibling::td/text()'
        ).get()

        item["category"] = response.xpath(
            '//ul[@class="breadcrumb"]/li[2]/a/text()'
        ).get()

        raw_image = response.xpath(
            '//div[contains(@class, "item") and contains(@class, "active")]/img/@src'
        ).get()
        item["image_url"] = response.urljoin(raw_image)

        # Convertir l'adresse en liste
        item["image_urls"] = [item["image_url"]] if item["image_url"] else []

        yield item