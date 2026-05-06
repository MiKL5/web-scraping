# **QuotesAPI**<a href="https://github.com/MiKL5/web-scraping/"><img align="right" src="../../assets/atomicWebScraping.png" alt="Web scraping" height="64px"></a>
<div align="center">

![Python](https://img.shields.io/badge/python-3.13-blue?style=flat&logo=python&logoColor=FFD43B) 
![Scrapy](https://img.shields.io/badge/Scrapy-API_Scraping-5E8862?style=flat&logo=scrapy&logoColor=white) 
![Pandas](https://img.shields.io/badge/pandas-Export_Multi-150458?style=flat&logo=pandas&logoColor=white) 
![JSON](https://img.shields.io/badge/JSON-API-000000?style=flat&logo=json&logoColor=white) 
![CSV](https://img.shields.io/badge/CSV-Export-007ACC?style=flat&logo=csv&logoColor=white) 
![Excel](https://img.shields.io/badge/Excel-XLSX-217346?style=flat&logo=excel&logoColor=white) 
![Parquet](https://img.shields.io/badge/Parquet-Apache-575E61?style=flat&logo=apacheparquet&logoColor=white)

</div><hr>

Ce spider Scrapy récupère les citations de l'API publique [quotes.toscrape.com/api/quotes](https://quotes.toscrape.com/api/quotes) avec pagination automatique et génère par Pandas **12 formats d'export** simultanés.
## **Les principales fonctionnalités**
* **Scraping API JSON** avec parsing automatique et gestion d'erreurs
* **Pagination infinie** via `has_next` et calcul dynamique de la page suivante
* **Extraction structurée** : auteur, lien auteur, tags, citation
* **Export massif automatique** dans 12 formats populaires lors de la fermeture du spider
* **Stockage mémoire** (`self.crawled_data`) pour traitement final Pandas
## **Les flux de données**
API JSON → Scrapy Item → Stockage mémoire → `closed()` → Pandas DataFrame → 12 Formats Export
### **Les champs récupérés sont**
Champ | Source JSON | Type
---|---|---
`author` | `quote.author.name` | String
`authorLink` | `quote.author.link` | URL
`tags` | `quote.tags` | Liste
`citation` | `quote.text` | String
## **Pagination intelligente**
```py
if parse_json["has_next"]:
next_pageUrl = f"https://quotes.toscrape.com/api/quotes?page={current_page + 1}"
yield scrapy.Request(url=next_pageUrl, callback=self.parse)
```
* Détection via `has_next` boolean
* URL dynamique avec incrémentation automatique
* Callback récursif sur `self.parse`
## **Export multi-formats (méthode `closed()`)**
Format | Extension | Commande Pandas
---|---|---
CSV | `.csv` | `df.to_csv()`
JSON | `.json` | `df.to_json(orient="records")`
Excel | `.xlsx` | `df.to_excel()`
Parquet | `.parquet` | `df.to_parquet()`
Feather | `.feather` | `df.to_feather()`
Pickle | `.pkl` | `df.to_pickle()`
HTML | `.html` | `df.to_html()`
Markdown | `.md` | `df.to_markdown()`
LaTeX | `.tex` | `df.to_latex()`
Texte | `.txt` | `with open("export/quotes.txt", "w", encoding="utf-8") as f:`<br>`f.write(df.to_string(index=False))`
NumPy | `.npy` | `df.to_numpy().tofile()`
XML | `.xml` | `df.to_xml()`

*Dossier de sortie : `export/`*
## Installation & exécution
```py
pip install scrapy pandas openpyxl pyarrow fastparquet
```
*Le spider s'arrête automatiquement après toutes les pages et génère tous les exports*

**settings.py recommandés :**
```txt
FEED_EXPORT_ENCODING = 'utf-8'
ROBOTSTXT_OBEY = True
```
## **La gestion d'erreurs est robuste**
* `try/except JSONDecodeError` : Logging des pages API invalides
* `quote.get()` sécurisé : Gestion des clés manquantes
* `closed()` avec `try/except` : Export même en cas d'erreur partielle
* Logging Scrapy natif pour debugging
## **Les avantages de cette approche**
* **Zéro configuration** : Exports simultanés dans tous les formats
* **API-first** : Parsing JSON natif, pas de XPath/CSS
* **Production-ready** : Gestion complète des erreurs
* **Data Science ready** : Formats Parquet/Feather/Pickle optimisés
* **Documentation ready** : HTML/Markdown/LaTeX inclus
## **Exemple de données exportées**
```json
{
"author": "Albert Einstein",
"authorLink": "https://quotes.toscrape.com/authors/albert-einstein",
"tags": ["change", "deep-thoughts"],
"citation": "The world as we have created it is a process of our thinking."
}
```
<!--## Extensions possibles
* Filtrage par tags/auteur via paramètres CLI
* Enrichissement via liens auteurs
* Pipeline de nettoyage/déduplication
* Dashboard Streamlit pour visualisation
* Base de données (PostgreSQL/MongoDB)-->
## **Les références officielles**
* [Scrapy Spiders](https://docs.scrapy.org/en/latest/topics/spiders.html)
* [Scrapy Lifecycle (closed)](https://docs.scrapy.org/en/latest/topics/spiders.html#spider-closed)
* [Pandas Export Formats](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)
* [quotes.toscrape.com API](https://quotes.toscrape.com/api/quotes?page=1)

<!--_Spider professionnel pour scraping API avec export Data Science complet en un clic._