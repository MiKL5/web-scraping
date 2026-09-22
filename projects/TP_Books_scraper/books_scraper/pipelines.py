import re
from   scrapy.pipelines.images import ImagesPipeline


STAR_RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksScraperPipeline:
    # Nettoie et type chaque BookItem avant son export

    def process_item(self, item, spider):
        item["price"] = self._clean_price(item.get("price"))
        item["star_rating"] = self._clean_star_rating(item.get("star_rating"))
        item["in_stock"] = self._clean_in_stock(item.get("in_stock"))
        item["number_available"] = self._clean_number_available(
            item.get("number_available")
        )
        item["description"] = self._clean_description(item.get("description"))
        return item

    @staticmethod
    def _clean_price(raw_price):
        # Nettoyer le prix
        if raw_price is None:
            return None
        cleaned = re.sub(r"[^\d.]", "", raw_price)
        return float(cleaned) if cleaned else None

    @staticmethod
    def _clean_star_rating(raw_rating_class):
        # Convertir les étoiles en nombre
        if raw_rating_class is None:
            return None
        for word, value in STAR_RATING_MAP.items():
            if word in raw_rating_class:
                return value
        return None

    @staticmethod
    def _clean_in_stock(raw_stock_text):
        # Vérifier le stock
        if raw_stock_text is None:
            return False
        return "In stock" in raw_stock_text

    @staticmethod
    def _clean_number_available(raw_availability_text):
        # Extraire le nombre d'exemplaires disponibles
        if raw_availability_text is None:
            return None
        match = re.search(r"(\d+)", raw_availability_text)
        return int(match.group(1)) if match else None

    @staticmethod
    def _clean_description(raw_description):
        # Nettoyer la description
        if not raw_description:
            return None
        return re.sub(r"\s+", " ", raw_description).strip()

# Enrigister les images
class BooksScraperImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        default_path = super().file_path(request, response=response, info=info, item=item)
        return default_path.split("/")[-1]