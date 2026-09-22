BOT_NAME = "books_scraper"

SPIDER_MODULES   = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

# Respecter robots.txt
ROBOTSTXT_OBEY = True

# Délai entre deux requêtes.
DOWNLOAD_DELAY = 0.5

# Encoder les fichiers exportés
FEED_EXPORT_ENCODING = "utf-8-sig"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR                      = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

ITEM_PIPELINES = {
    "books_scraper.pipelines.BooksScraperPipeline": 300,
    "books_scraper.pipelines.BooksScraperImagesPipeline": 400,
}

IMAGES_STORE        = "images"     # dossier
IMAGES_URLS_FIELD   = "image_urls"
IMAGES_RESULT_FIELD = "images"