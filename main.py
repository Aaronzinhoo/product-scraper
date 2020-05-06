from pathlib import Path

from config import get_args
from productscraperfactory import product_scrapers, URLS

def main(source, url, root):
    sources = ['brandi' , 'wconcept', 'mwusinsa']
    for source in sources:
        source_directory = root+'/'+source
        Path(source_directory).mkdir(parents=True, exist_ok=True)
        product_scraper = product_scrapers.get_scraper(source, url, source_directory)
        product_scraper.scrape_products()
    
        
if __name__ == '__main__':
    main(**vars(get_args()))
