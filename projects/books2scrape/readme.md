# Web Scraping de livres sur books.toscrape.com avec Scrapy<a href="https://github.com/MiKL5/web-scraping/"><img align="right" src="../../assets/atomicWebScraping.png" alt="Web scraping" height="64px"></a>
<div align="center">

![Python](https://img.shields.io/badge/python-3.13-blue?style=flat&logo=python&logoColor=FFD43B) 
![Scrapy](https://img.shields.io/badge/Scrapy-Web_Scraping-5E8862?style=flat&logo=scrapy&logoColor=white)

</div><hr>

Il s'agit d'un spider Scrapy visant à extraire automatiquement des informations bibliographiques (titre, prix, image, ...) depuis le site de démonstration [books.toscrape.com](https://books.toscrape.com/).  
Le but est de collecter et structurer les données pour chaque livre d’une page principale.
---
## **Le fonctionnement avec le langage de requête "xpath"**

<details>
<sumary><h2><b>Le fonctionnement avec le langage de requête "xpath"</b></h2></sumarr>

1. **Collecte des blocs de livres** avec la requête XPath sur la classe de chaque livre (`//li[@class="col-xs-6 col-sm-4 col-md-3 col-lg-3"]`).
2. **Extraction des informations** pour chaque livre :
   * Titre (`.//h3/a/@title`)
   * Prix (`.//p[@class="price_color"]/text()`)
   * Source de l’image (`.//img/@src`)
3. **Astuces XPath** documentées dans le fichier pour manipuler descendants, attributs, siblings, etc.
### **Notes**
* La syntaxe `.//` dans les XPaths cible des descendants à partir d’un noeud local (ex: un bloc livre).
* Les méthodes `.get()`, `.getall()`, `.extract()`, etc., selon le nombre de valeurs attendues.
* Pour extraire « le premier » élément, utiliser `[0]` ou `.get()` ; pour tous, `.getall()`.
### **Références**
[Documentation officielle Scrapy](https://docs.scrapy.org/)  
[XPath Cheatsheet](https://devhints.io/xpath)
[Scrapy Crawl Spider - A Complete Guide](https://www.youtube.com/watch?v=MaPyt6dpnVY)

</details>

___
## **Le fonctionnement avec le "CSS"**

<details>

* Récupération des prix des livres présents avec le sélecteur CSS `p.price_color`.
* Envoi des résultats sous forme de dictionnaire contenant le prix extrait.
### **Notes**
* Le sélecteur CSS `p.price_color::text` cible le texte du prix pour chaque livre.
* Le spider explore uniquement la page d’accueil dans cette version.
### **Références**
[CSS Selectors Reference](https://developer.mozilla.org/fr/docs/Web/CSS/CSS_Selectors)

</details>

___
## **Exporter les données**

<details>

* En "json" ➜ `scrapy runspider b2s -o data.json`
  * Faire '`ctrl` + `A` + `K` + `F`' pour l'indentation.
* En "csv" ➜ `scrapy runspider b2s -o data.csv`

Dans "settings", '`FEED_EXPORT_ENCODING = 'utf-8'`' encode les caractères.  
### **Références**
[Documentation officielle Scrapy - Feed Exports](https://docs.scrapy.org/en/latest/topics/feed-exports.html)  
[Documentation officielle Scrapy - Item Exporters](https://docs.scrapy.org/en/latest/topics/item-exporters.html)  
[Documentation officielle Scrapy - Commandes CLI](https://docs.scrapy.org/en/latest/topics/commands.html#running-spiders)  
[Documentation officielle Scrapy - Paramètre FEED_EXPORT_ENCODING](https://docs.scrapy.org/en/latest/topics/settings.html#feed-export-encoding)

</details>

___
## **Récupérer les données sur plusieurs pages**

<details>

### **Gestion de la pagination**
* Le lien vers la page suivante est extrait par `//li[@class='next']/a/@href`.
* Si ce lien existe, le spider construit l’URL suivante et continue jusqu’à la dernière page.
### **Parcours des pages de catalogue**
* Le spider récupère tous les blocs livres avec le XPath ➜ `//li[@class="col-xs-6 col-sm-4 col-md-3 col-lg-3"]`.
* Pour chaque bloc, il extrait le lien relatif vers la page du livre ➜ `.//h3/a/@href`.
* Il suit ce lien avec `response.follow` et démarche le parseur `parse_book_page`.
### **Extraire aux pages individuelles**
* Sur la page de chaque livre, les informations suivantes sont extraites avec XPath :
  * Titre ➜ `//h1/text()`.
  * Prix ➜ `//p[@class="price_color"]/text()`.
### **Références**
[Documentation officielle Scrapy - Parsing Pages with XPath](https://docs.scrapy.org/en/latest/topics/selectors.html)  
[Documentation officielle Scrapy - Follow Links Documentation](https://docs.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Request.follow)

</details>

___
## **Les "rules objects"**

<details>

### **L'utilité**
* Les objets rules dans Scrapy CrawlSpider définissent des règles automatiques pour :
* Extraire des liens spécifiques via LinkExtractor (XPath/CSS/régex)​
* Appliquer un callback pour parser les pages trouvées (ex: parse_item)​
* Utiliser `follow = True` pour continuer l'exploration récursive des liens extraits​
* Parcourir sites/pagination sans écrire manuellement les Request​
* Elles remplacent la méthode parse() manuelle pour un crawling structuré.
### **Selles du projet**
* Parcours complet de toutes les pages du catalogue via règles automatiques  
* Extraction détaillée sur chaque page livre :
    * Titre (//h1/text())
    * Prix (//p[@class='price_color']/text())
    * UPC/Product ID (//th[text()='UPC']/following-sibling::td/text())
    * Type de produit (//th[text()='Product Type']/following-sibling::td/text())
    * Stock/Disponibilité (//th[text()='Availability']/following-sibling::td/text())
* Double règle de navigation intelligente :
    * Suivi des liens livres avec extraction (parse_item)
    * Pagination automatique (next)

### **Références**
[Scrapy - CrawlSpider & Rules](https://docs.scrapy.org/en/latest/topics/spiders.html#crawlspider)  
[Following LINKS Automatically with Scrapy CrawlSpider](https://www.youtube.com/watch?v=o1g8prnkuiQ)
</details>

___
## **Les chargeurs d'articles**

<details>

### **Définition**
Les Item Loaders dans Scrapy sont des objets conçus pour faciliter et standardiser la collecte, le nettoyage et la transformation des données extraites avant de les stocker dans des Items.
Ils permettent d’associer à chaque champ (field) des fonctions de traitement en entrée (input processors) et en sortie (output processors), ce qui rend le code de scraping plus modulaire et maintenable.
Par exemple, ils peuvent nettoyer du texte, convertir des formats, concaténer plusieurs valeurs extraites sous une même clé, ou filtrer les données inutiles.
Pour remplir un Item avec un Item Loader, on utilise des méthodes comme add_xpath(), add_css() ou add_value() qui extraient ou assignent des valeurs, toujours traitées par les processeurs définis.
Enfin, la méthode load_item() retourne l’Item final, prêt à être renvoyé ou exporté.
Les Item Loaders allègent ainsi la logique dans les spiders et favorisent la réutilisation de règles de nettoyage entre projets ou spiders différents.
### **Les avantages d'itemLoader**
* Centralisation des règles de nettoyage dans items.py
* Réutilisabilité des processors entre spiders
* Utiliser `add_xpath()` au lieu de `xpath().get()` est plus propre
* Gestion automatique des valeurs None/vides
* Validation et transformation standardisées
### **Références**
[Scrapy Item Loaders officiel](https://docs.scrapy.org/en/latest/topics/loaders.html)  
[Explications détaillées GeeksforGeeks](https://www.geeksforgeeks.org/python/scrapy-item-loaders/)  
[Tutoriel vidéo Scrapy Items & Item Loaders](https://www.youtube.com/watch?v=NWBso2Jv4Ug)

</details>