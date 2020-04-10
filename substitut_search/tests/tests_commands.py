from unittest.mock import Mock
from unittest import skip

from django.test import TestCase

from ..models import Product
from ..utils.fill_db import FillDB

nutrients = ['fat', 'saturated-fat', 'sugars', 'salt']

class TestFillDB(TestCase):
    MOCK_PRODUCTS = [
        {
            "code": "125547",
            "nutrition_grade_fr": "a",
            "categories_tags": ["en:test"],
            "product_name": "test1",
            "url": "https//test.com",
            "image_front_small_url": "https//test.com",
            "nutrient_levels": {e: "low" for e in nutrients},
            'nutriments': {e+'_100g': '2' for e in nutrients}
        }, {
            "code": "243547",
            "nutrition_grade_fr": "b",
            "categories_tags": ["en:test"],
            "product_name": "test2",
            "url": "https//test2.com",
            "image_front_small_url": "https//test2.com"
        },
    ]

    # test insert mocked products
    def test_insert_products(self):
        self.assertEqual(Product.objects.count(), 0)
        fill_db = FillDB()
        fill_db.dl_products = Mock(return_value=self.MOCK_PRODUCTS)
        fill_db.insert_products()
        fill_db.dl_products.assert_called_once()
        self.assertQuerysetEqual(
            list(Product.objects.all()),
            ['<Product: Test1>', '<Product: Test2>'])

    # test download and insert products
    @skip("very long test using API call")
    def test_insert_products_no_mock(self):
        self.assertEqual(Product.objects.count(), 0)
        fill_db = FillDB()
        fill_db.insert_products()
        self.assertGreater(Product.objects.count(), 200)

class TestUpdateDB(TestCase):
    fixtures = ['products']
    MOCK_PRODUCTS = [
        {
            "code": "246825",
            "nutrition_grade_fr": "a",
            "categories_tags": ["en:testUpdate"],
            "product_name": "test one",
            "url": "https//test.com",
            "image_front_small_url": "https//test.com",
            "nutrient_levels": {e: "low" for e in nutrients},
            'nutriments': {e+'_100g': '3' for e in nutrients}
        }, {
            "code": "459562",
            "nutrition_grade_fr": "b",
            "categories_tags": ["en:testUpdate"],
            "product_name": "test two",
            "url": "https//test2.com",
            "image_front_small_url": "https//test2.com",
            "nutrient_levels": {e: "low" for e in nutrients},
            'nutriments': {e+'_100g': '1' for e in nutrients}
        },
    ]

    #test product updated
    def test_update_product(self):
        self.assertQuerysetEqual(list(Product.objects.all()), ['<Product: test1>','<Product: test2>'])
        fill_db = FillDB()
        fill_db.dl_products = Mock(return_value=self.MOCK_PRODUCTS)
        fill_db.update_products()
        fill_db.dl_products.assert_called_once()
        self.assertQuerysetEqual(
            list(Product.objects.all()),
            ['<Product: Test One>', '<Product: Test Two>'])
