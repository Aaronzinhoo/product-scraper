import csv
import time
import json
import random
from pathlib import Path
from datetime import datetime
from abc import abstractmethod

import requests

from bs4 import BeautifulSoup
from termcolor import cprint


class ProductScraper():
    date = str(datetime.now().date()).replace('-','_')
    
    def __init__(self, source, root='./'):
        self._source = source
        self._root = root

    @abstractmethod
    def find_image(self, product):
        pass

    @abstractmethod
    def find_base_price(self, product):
        pass

    @abstractmethod
    def find_name(self, product):
        pass

    @abstractmethod
    def get_product_info(self, product):
        return {
                "base_price": self.find_base_price(product),
                "product_name": self.find_name(product),
            }

    @abstractmethod
    def find_products(self):
        pass
    
    def scrape_products(self):
        products_info = []
        image_urls = []
        products = self.find_products()
        for rank, product in enumerate(products, start=1):
            product_info = {'rank': rank, **self.get_product_info(product)}
            image_urls.append(self.find_image(product))
            products_info.append(product_info)
        self.to_csv(products_info)
        self.image_downloader(image_urls)
    
    def to_csv(self, product_info):
        print(Path(self._root))
        with open(Path(self._root) / (self.date + '_' + self._source + "_ranking.csv"), 'w',
                  encoding='utf-8-sig') as f:
            fieldnames = list(product_info[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(product_info)

    @staticmethod
    def print_in_color(text, color):
        """ Prints `text` in passed `color` """
        cprint(text, color)

    def image_downloader(self, image_urls):
        """ Downloads images """

        output_dir = Path(self._root) / (self.date + '_'  + self._source + '_images')
        output_dir.mkdir(exist_ok=True, parents=True)

        for rank, image_url in enumerate(image_urls, start=1):
            download_path = output_dir / (str(rank)+'.jpg')
            self.print_in_color(f"Downloading {str(rank)}...........", "yellow")
            response = requests.get(image_url, stream=True)
            if response.status_code == 200 or response.status_code == 206:
                response.raw.decode_content = True
                with open(download_path, 'wb') as fobj:
                    self.print_in_color(f"{rank}.jpg downloaded.\n", "green")
                    fobj.write(response.content)
            else:
                self.print_in_color(f"{rank}.jpg not downloaded.\n", "red")
            time.sleep(random.randint(1, 5))


class MwusinsaProductScraper(ProductScraper):
    def __init__(self, source, url, root='./'):
        super().__init__(source, root)
        self._url = url

    def find_products(self):
        page = requests.get(self._url).content
        content = BeautifulSoup(page)
        return content.find_all('li', {'class':'prd-block'})

    def find_name(self, product):
        return product.find('a', {'class':'name'}).text.strip()

    def find_base_price(self, product):
        value_text = product.find('div', {'class':'price'}).a.text
        return ''.join(s for s in value_text if s.isdigit())

    def find_image(self, product):
        return 'http:' + product.find('div',{'class':'img-block'}).img["src"]

class BrandiProductScraper(ProductScraper):
    headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36' , 'content-type':'application/x-www-form-urlencoded; charset=utf-8', 'authorization':'3b17176f2eb5fdffb9bafdcc3e4bc192b013813caddccd0aad20c23ed272f076_1423639497'}
    
    def __init__(self, source, url, root='./'):
        super().__init__(source, root)
        self._url = url
        
    def find_products(self):
        page = requests.get(self._url, headers=self.headers).content
        content = json.loads(page.decode('utf-8'))
        return content["data"]

    def find_name(self, product):
        return product["name"]

    def find_base_price(self, product):
        return product["price"]

    def find_sale_price(self, product):
        return product["sale_price"]
    
    def find_image(self, product):
        return product["image_url"]

    def get_product_info(self, product):
        return {"sale_price": self.find_sale_price(product),
                **super().get_product_info(product)}

class WconceptProductScraper(ProductScraper):

    def __init__(self, source, url, root='./'):
        super().__init__(source, root)
        self._url = url
    
    def find_products(self):
        page = requests.get(self._url).content
        content = BeautifulSoup(page)
        products = content.find_all('div', {'class':'thumbnail_list'})
        return (products[0].find_all('li') + products[1].find_all('li'))

    def find_name(self, product):
        return product.find('div', {'class':'product'}).text.strip()

    def find_base_price(self, product):
        return product.find('span', {'class':'discount_price'}).text
    
    def find_price(self, product):
        try:
            return product.find('span', {'class':'base_price'}).text
        except Exception as e:
            return None

    def find_image(self, product):
        return 'http:' + product.find('div',{'class':'img'}).img["src"]

    def get_product_info(self, product):
        info = super().get_product_info(product)
        # this price can be base or sale price
        price = info["base_price"]
        # if this price is found then the base price is actually sale_price
        base_price = self.find_price(product)
        if base_price:
            info["sale_price"] = price
            info["base_price"] = base_price
        else:
            info["sale_price"] = ""
        return info
