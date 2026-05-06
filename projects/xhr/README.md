# XHR Spider - Scraper de citations par Le filtrage dynamique<a href="https://github.com/MiKL5/web-scraping/"><img align="right" src="../../assets/atomicWebScraping.png" alt="Web scraping" height="64px"></a>
<div align="center">

![Python](https://img.shields.io/badge/Python-3.13.9-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Scrapy](https://img.shields.io/badge/Scrapy-2.13.4-60A839?style=for-the-badge&logo=scrapy&logoColor=white)
![XPath](https://img.shields.io/badge/XPath-2.0-orange?style=for-the-badge)
![ASP.NET](https://img.shields.io/badge/ASP.NET-VIEWSTATE-512BD4?style=for-the-badge&logo=dotnet&logoColor=white)

</div><hr>

L'API JavaScript "`XMLHttpRequest`" est intégrée aux navigateurs permettant d’envoyer des requêtes HTTP ou HTTPS de manière asynchrone ; sans recharger la page entière.  
Le but est d'extraire des citations filtrées par auteur et tag depuis quotes.toscrape.com avec gestion du `VIEWSTATE` "ASP.NET" et pagination automatique.
---
## **Les fonctionnalités**
* **Filtrage dynamique** par auteur et tag via paramètres CLI
* **Gestion du '`VIEWSTATE`'** (protection CSRF ASP.NET)
* **Pagination automatique** pour scraper tous les résultats
* **Logs enrichis** avec des informations détaillées
* **Gestion d'erreurs** robuste avec '`errback'`
* **Nettoyage automatique** des guillemets
* **Paramètres configurables** sans modifier le code
* **Export multi-formats** (`JSON`, `CSV`, `XML`, `JSONL`)
* **Async/await support** (Scrapy 2.13+)
## **Les technologies**
### Le stack principal
Technologie | Version | Rôle | Badge
---|---|---|---
**Python** | 3.13.9 | Langage de programmation | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
**Scrapy** | 2.13.4 | Framework de web scraping | ![Scrapy](https://img.shields.io/badge/Scrapy-60A839?logo=scrapy&logoColor=white)
**lxml** | 6.0.2 | Parser HTML/XML | ![lxml](https://img.shields.io/badge/lxml-orange)
**Twisted** | 25.5.0 | Framework réseau asynchrone | ![Twisted](https://img.shields.io/badge/Twisted-purple)
### Les protocoles & standards
Standard | Usage |
---|---
![XPath](https://img.shields.io/badge/XPath-2.0-orange) | Sélection d'éléments DOM
![HTTP](https://img.shields.io/badge/HTTP-1.1%2F2.0-blue) | Protocole de communication
![POST](https://img.shields.io/badge/Method-POST-red) | Soumission de formulaires
![ASP.NET](https://img.shields.io/badge/ASP.NET-VIEWSTATE-512BD4?logo=dotnet) | Gestion d'état côté serveur
## **Les prérequis**
* **Python** >= 3.8
* **pip** >= 21.0
* **Git** (optionnel)
## 📦 Installation
```bash
pip install -r requirements.txt
```
## **L'utiliser**
```bash
scrapy crawl xhr_spider.py -O data.json
```
## **L'architecture**
### Le flux de fonctionnement
```mermaid
graph TD
    A[start] --> B[GET /search.aspx]
    B --> C{VIEWSTATE trouvé?}
    C -->|Non| D[Log erreur + Stop]
    C -->|Oui| E[POST /filter.aspx avec paramètres]
    E --> F[Parse réponse]
    F --> G{Citations trouvées?}
    G -->|Non| H[Log warning + Stop]
    G -->|Oui| I[Extraire données]
    I --> J{Page suivante existe?}
    J -->|Oui| E
    J -->|Non| K[Fin]
```
### **Le diagramme de séquence**
```mermaid
sequenceDiagram
    participant Spider
    participant Website
    participant Data
    
    Note over Spider: start() appelé
    Spider->>Website: GET /search.aspx
    activate Website
    Website-->>Spider: HTML + Formulaire + VIEWSTATE
    deactivate Website
    
    Note over Spider: filter() - Extraction VIEWSTATE
    
    Spider->>Website: POST /filter.aspx<br/>(author, tag, VIEWSTATE)
    activate Website
    Note over Website: Validation formulaire<br/>Filtrage des citations
    Website-->>Spider: 302 Redirect ou HTML citations
    deactivate Website
    
    Note over Spider: parse() - Extraction données
    
    loop Pour chaque citation
        Spider->>Spider: XPath extraction<br/>(text, author, tags)
        Spider->>Spider: Nettoyage guillemets
        Spider->>Data: yield item
        activate Data
        Data-->>Spider: Item enregistré
        deactivate Data
    end
    
    alt Page suivante existe
        Spider->>Website: GET /page/2
        activate Website
        Website-->>Spider: HTML page suivante
        deactivate Website
        Note over Spider: Retour à parse()
    else Dernière page
        Note over Spider: ✅ Scraping terminé
    end
    
    Note over Data: Export final<br/>(JSON/CSV/XML)
```
### **La structure du projet**
```python
class XhrSpiderSpider(scrapy.Spider):
    │
    ├── __init__()          # Initialisation avec paramètres CLI
    │
    ├── start()             # Point d'entrée (async)
    │   └── GET /search.aspx
    │
    ├── filter()            # Extraction VIEWSTATE + POST formulaire
    │   ├── Extraire VIEWSTATE
    │   └── FormRequest avec formdata
    │
    ├── parse()             # Parser les résultats
    │   ├── Extraire citations
    │   ├── Nettoyer données
    │   └── Suivre pagination
    │
    └── handle_error()      # Gestion des erreurs réseau
```
## **La configuration**
### **Les paramètres du spider**
Paramètre | Type | Défaut | Description
---|---|---|---
`author` | str | "J.K. Rowling" | Auteur à rechercher
`tag` | str | "dumbledore" | Tag à filtrer
### **Les settings personnalisés**
```python
custom_settings = {
    'DOWNLOAD_DELAY'                : 1,              # Délai entre requêtes (secondes)
    'CONCURRENT_REQUESTS_PER_DOMAIN': 1,              # Nombre de requêtes parallèles
    'ROBOTSTXT_OBEY'                : True,           # Respecter robots.txt
    'FEED_EXPORT_ENCODING'          : 'utf-8'         # Encodage des exports
}
```
### Modifier les settings globaux
Éditez `settings.py` :
```python
# Rate limiting
DOWNLOAD_DELAY           =  2  # Plus lent et plus sûr
AUTOTHROTTLE_ENABLED     = True
AUTOTHROTTLE_START_DELAY =  1
AUTOTHROTTLE_MAX_DELAY   = 10

# User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

# Logs
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
```
## **Dépannage**
### **Le problème 1 : Une `SyntaxError` avec les guillemets**
**Erreur :**
```sh
SyntaxError: unterminated string literal (detected at line 84)
text = text.strip('"'')
```
**Solution :**
```py
# ❌ Incorrect
text = text.strip('"'')

# ✅ Correct
text = text.strip('"')
```
### **Le problème 2 : VIEWSTATE non trouvé**
**Logs :**
```
[xhr_spider] ERROR: ❌ VIEWSTATE n'est pas trouvé
```
**Causes possibles :**
1. URL incorrecte (vérifier `/search.aspx`)
2. Structure HTML changée
3. Site bloque le scraping
**Debug :**
```py
def filter(self, response):
    # Afficher le HTML brut
    self.logger.debug(response.text[:1000])
    
    # Tester différents sélecteurs
    viewstate = response.xpath("//input[@name='__VIEWSTATE']/@value").get()
    if not viewstate:
        viewstate = response.css("input[name='__VIEWSTATE']::attr(value)").get()
```
### **Le problème 3 : Aucune citation trouvée**
**Logs :**
```
[xhr_spider] WARNING: ⚠️ Aucune citation trouvée pour Einstein / science
```
**Solutions :**
1. Vérifier l'orthographe de l'auteur
2. Vérifier que le tag existe
3. Inspecter la réponse HTML
**Debug :**
```py
def parse(self, response):
    # Sauvegarder la page pour inspection
    with open('debug.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
```
### **Le problème 4 : Bloqué par le serveur (403/429)**
**Solutions :**
**1. Augmenter le délai :**
```sh
scrapy runspider xhr_spider.py -s DOWNLOAD_DELAY=3
```
**2. Changer le User-Agent :**
```py
custom_settings = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
```
**3. Activer AutoThrottle :**
```py
custom_settings = {
    'AUTOTHROTTLE_ENABLED'    : True,
    'AUTOTHROTTLE_START_DELAY':  2,
    'AUTOTHROTTLE_MAX_DELAY'  : 10
}
```
## **Les performances**
### **Les métriques typiques**
Métrique | Valeur
---|---
Pages/minute | ~60 (avec DOWNLOAD_DELAY=1)
Citations/minute | ~300-600
Temps moyen/page | 1-2 secondes
Taux de succès | >95%
### **L'optimisation**
**Pour des volumes importants :**
```py
custom_settings = {
    'CONCURRENT_REQUESTS'           : 16,
    'CONCURRENT_REQUESTS_PER_DOMAIN':  4,
    'DOWNLOAD_DELAY'                : .5,
    'AUTOTHROTTLE_ENABLED'          : True
}
```