# **Quotes**<a href="https://github.com/MiKL5/web-scraping/"><img align="right" src="../../assets/atomicWebScraping.png" alt="Web scraping" height="64px"></a>
<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-HTTP%20client-2ea44f)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-HTML%20parsing-4E9A06)
![pandas](https://img.shields.io/badge/pandas-Data%20analysis-150458?logo=pandas)
![lxml](https://img.shields.io/badge/lxml-XML%2FHTML%20parser-0A7BBB)
![openpyxl](https://img.shields.io/badge/openpyxl-Excel%20writer-207245)


</div>

"**Quotes**" est un petit projet de web scraping en Python qui extrait des citations du site [https://quotes.toscrape.com](https://quotes.toscrape.com) et les enregistre dans plusieurs formats pour une analyse ou une réutilisation ultérieure.
## **Les fonctionnalités**
* Récupération automatique des citations sur plusieurs pages du site `quotes.toscrape.com`.  
* Extraction de la citation, de l’auteur et des tags associés.  
* Sauvegarde des données dans trois formats :
    * `quotes.csv`
    * `quotes.xlsx`
    * `quotes_df.json`
## **Les prérequis**
* Python 3.9 ou plus récent.
## **Installer les dépendances**
```sh
pip install -r requirements.txt
```
## **L'utilisation**
Le script principal se trouve dans `quotes.py`. Il envoie des requêtes HTTP à `https://quotes.toscrape.com/`, parcourt les pages tant qu’il trouve des citations, puis enregistre le résultat dans le dossier `projects/quotes`.  
Exécuter
```sh
python quotes.py
```
Trois seront créés :
* `projects/quotes/quotes.csv`
* `projects/quotes/quotes.xlsx`
* `projects/quotes/quotes_df.json`

## **La structure du projet**
```txt
Quotes/
├─ quotes.py
├─ requirements.txt
├─ README.md
└─ projects/
└─ quotes/
├─ quotes.csv
├─ quotes.xlsx
└─ quotes_df.json
```
Le dossier `projects/quotes` doit exister (ou sera à créer) afin d’éviter des erreurs lors de l’écriture des fichiers de sortie.
## **Les détails techniques**
Le script utilise :
* `requests` pour télécharger le HTML de chaque page.
* `BeautifulSoup` (parser `lxml`) pour extraire les blocs de citations et les champs texte.
* `pandas` pour convertir la liste de dictionnaires en `DataFrame` puis exporter vers CSV, Excel et JSON.
### **Les fonctions principales**
* `get_quotes(pageUrl)` : télécharge et parse une page, renvoie une liste de citations (ou `None` si aucune citation n’est trouvée).
* `extract_data(div_quotes)` : extrait `quote`, `author` et `tags` à partir d’un bloc HTML `<div class="quote">`.

La pagination est gérée par une boucle qui construit les URLs de la forme `https://quotes.toscrape.com/page/{i}/` et s’arrête dès qu’une page ne contient plus de citations.
## **Les bonnes pratiques et respect du site**
Ce projet est pédagogique.  
Le site "quotes.toscrape.com" est spécialement conçu pour l’apprentissage du web scraping, ce qui en fait une cible idéale pour des exercices. Nonobstant :
*  Ne pas lancer le script de manière abusive ou en boucle infinie.  
*  Adapter la fréquence des requêtes si nécessaire.