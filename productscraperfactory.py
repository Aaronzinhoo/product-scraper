from productscraper import WconceptProductScraper, \
    BrandiProductScraper,\
    MwusinsaProductScraper

URLS = {
    "wconcept": "https://www.wconcept.co.kr/TopSeller?mcd=m33439436",
    "brandi": "https://cf-api-c.brandi.me/v1/web/products?offset=0&type=best&store-type=1&order=weekly",
    "mwusinsa": "https://mwusinsa.musinsa.com/app/contents/bestranking/?price2=&price1=&d_cat_cd=&u_cat_cd=&range=nw&price=&sale_goods=&new_product_yn=Y&list_kind=&page=1&display_cnt=100&popup=&sale_rate=&range=nw"
}

class ProductScraperFactory():
    def __init__(self):
        self._scrapers = {}
        
    def register_scraper(self, site, scraper):
        self._scrapers[site] = scraper
        
    def get_scraper(self, site, url=None, root='./'):
        scraper = self._scrapers.get(site)
        if not scraper:
            raise ValueError(site)
        if not url:
            url = URLS.get(site)
        return scraper(site, url, root)

product_scrapers = ProductScraperFactory()
product_scrapers.register_scraper('brandi', BrandiProductScraper)
product_scrapers.register_scraper('wconcept', WconceptProductScraper)
product_scrapers.register_scraper('mwusinsa', MwusinsaProductScraper)
