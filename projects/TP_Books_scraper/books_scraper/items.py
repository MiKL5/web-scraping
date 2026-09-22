import scrapy


class BookItem(scrapy.Item):
    # Champs de la page catalogue
    title         = scrapy.Field()
    price         = scrapy.Field()
    star_rating   = scrapy.Field()
    in_stock      = scrapy.Field()
    thumbnail_url = scrapy.Field()
    detail_url    = scrapy.Field()

    # Champs de la page de détail
    upc              = scrapy.Field()
    description      = scrapy.Field()
    number_available = scrapy.Field()
    category         = scrapy.Field()
    image_url        = scrapy.Field()

    # Télécharger les images
    image_urls = scrapy.Field()
    images     = scrapy.Field()