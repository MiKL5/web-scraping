# TP Books_scraper
<div align="center">

![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=flat&logo=python&logoColor=white) ![Scrapy](https://img.shields.io/badge/Scrapy-2.11-60A839?style=flat&logo=scrapy&logoColor=white) ![XPath](https://img.shields.io/badge/Selectors-XPath-orange?style=flat)  ![Pillow](https://img.shields.io/badge/Pillow-Images-yellowgreen?style=flat)

</div>

`Books_scraper` est un crawler [Scrapy](https://scrapy.org/) parcourant le catalogue de [books.toscrape.com](https://books.toscrape.com/). Il suit la page de détail des livres. Exporte un jeu de données structuré.  
La pagination est découverte dynamiquement à partir du lien **next** présent dans le HTML, et les sélecteurs du projet sont exprimés en **XPath**.
---
### Données collectées
Champ | Origine | Description
---|:-:|---
`title` | Catalogue | Titre du livre
`price` | Catalogue | Prix (décimal, sans `£`)
`star_rating` | Catalogue | Note entre 1 et 5 (entier)
`in_stock` | Catalogue | Disponibilité (booléen)
`thumbnail_url` | Catalogue | URL absolue de la miniature
`detail_url` | Catalogue | URL absolue de la page de détail
`upc` | Détail | Identifiant UPC
`description` | Détail | Description du livre (espaces nettoyés)
`number_available` | Détail | Nombre exact d'exemplaires disponibles (entier)
`category` | Détail | Catégorie du livre
`image_urls` | Spider | Liste contenant `image_url`, lue par la pipeline de téléchargement
`images` | — | Métadonnées du téléchargement `BookHarvestImagesPipeline`

<details>
<summary>🗂️ Structure</summary>

```
TP_BookHarvest—Scrapy Edition/
│
├── scrapy.cfg
│
├── books_scraper/
│   ├── __init__.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── settings.py
│   │
│   └── spiders/
│       ├── __init__.py
│       └── books.py
│
├── images/
├── README.md
├── requirements.txt
└── books.csv
```

</details>

## Installer
```sh
pip install -r requirements.txt
```
## Lancer le spider
```sh
cd '/Volumes/Workbench/gh/wS/projects/TP_BookHarvest—Scrapy Edition'
scrapy crawl books -O books.csv
scrapy crawl books -O books.json
```
> L'option `-O` (majuscule) écrase le fichier de sortie ;
> `-o` (minuscule) ajoute les résultats.