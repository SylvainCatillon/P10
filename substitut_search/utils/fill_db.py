import requests

from django.db import IntegrityError, DataError, transaction

from ..models import Product


def trad(word):
    """Translate the nutriments information in french"""
    initial_words = [
        'saturated-fat', 'fat', 'sugars', 'salt',
        'low', 'moderate', 'high']
    trad_words = [
        'Acides gras saturés', 'Matières grasses', 'Sucres', 'Sel',
        'faible', 'modérée', 'élevée']
    return trad_words[initial_words.index(word)]


def get_nutrients(product):
    """Get the nutrients from an OpenFoodFact downloaded product,
    by getting the level and the quantity per 100g"""
    result = []
    for nutrient in ['fat', 'saturated-fat', 'sugars', 'salt']:
        try:
            level = product['nutrient_levels'][nutrient]
            quantity = product['nutriments'][nutrient+'_100g']
        except KeyError:
            continue
        # gerer string vide
        string = f"{trad(nutrient)} en quantitée {trad(level)} ({quantity}g)"
        result.append(string)
    return result


class FillDB:
    """Use this class to download products from fr.openfoodfacts.org
    and fill the database"""

    def __init__(self, nb_products=1000):
        self.nb_products = nb_products

    def dl_page(self, nb, page):
        """Download one page of products from OpenFoodfacts.org.
        Takes as args the page size as 'nb' and the page number as 'page'"""
        payload = {
            "sort_by": "unique_scans_n",
            "action": "process",
            "json": 1,
            "page_size": nb,
            "page": page}
        headers = {'user-agent': 'PurBeurre_WebApp - Version 1.0'}
        raw_result = requests.get(
            "https://fr.openfoodfacts.org/cgi/search.pl",
            params=payload,
            headers=headers)
        return raw_result.json()["products"]

    def dl_products(self):
        """Download the requested number of products from OpenFoodFacts.
        As the maximum page size is 1000, the function may need to launch
        the sub-function 'dl-page' several times"""
        products_list = []
        nb_products = self.nb_products
        page = 1
        #  The OpenFoodFacts maximum page size is 1000
        #  The loop will dl the products 1000 by 1000 while incrementing the
        #  page number, until the number of products left to dl is under 1000
        while nb_products > 1000:
            products_list += self.dl_page(1000, page)
            page += 1
            nb_products -= 1000
        products_list += self.dl_page(nb_products, page)
        return products_list

    def insert_products(self):
        """Launch 'dl_products' to download the products from OpenFoodfacts.org
        then insert the products in the database"""
        products_list = self.dl_products()
        for product in products_list:
            #  if the product doesn't contain the right info, go to the next
            try:
                code = product["code"]
                nutriscore = product["nutrition_grade_fr"].lower()
                categories = product["categories_tags"]
                name = product["product_name"].title()
                link = product["url"]
                image = product["image_front_small_url"]
            except KeyError as error:
                continue
            nutrient_levels = get_nutrients(product)
            #  if the product can't be inserted, go to the next
            try:
                with transaction.atomic():
                    Product.objects.create(
                        code=code,
                        nutriscore=nutriscore,
                        categories=categories,
                        name=name, link=link, image=image,
                        nutrient_levels=nutrient_levels)
            except (IntegrityError, DataError) as error:
                continue

    def update_products(self):
        """Launch 'dl_products' to download the products from OpenFoodfacts.org
        then update the products in the database"""
        products_list = self.dl_products()
        for product in products_list:
            #  if the product doesn't contain the right info, go to the next
            try:
                code = product["code"]
                nutriscore = product["nutrition_grade_fr"].lower()
                categories = product["categories_tags"]
                name = product["product_name"].title()
                link = product["url"]
                image = product["image_front_small_url"]
            except KeyError as error:
                continue
            nutrient_levels = get_nutrients(product)
            try:
                with transaction.atomic():
                    Product.objects.filter(code=product['code']).update(
                        nutriscore=nutriscore,
                        categories=categories,
                        name=name, link=link, image=image,
                        nutrient_levels=nutrient_levels)
            except (Product.DoesNotExist, IntegrityError, DataError) as error:
                print("Warning, catched error while updating the database: " + 
                    str(error))
                continue
