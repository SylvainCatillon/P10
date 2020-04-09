from unittest.mock import Mock
from unittest import skip

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


from ..models import Product
from ..utils.fill_db import FillDB

class TestFillDB(TestCase):
    nutrients = ['fat', 'saturated-fat', 'sugars', 'salt']
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

class TestSearchProduct(TestCase):
    fixtures = ['products']

    # test search a product by name
    def test_find_a_product(self):
        response = self.client.get(
            f"{reverse('substitut:search')}?query=test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context["products"]),
            len(Product.objects.filter(name__icontains='test')))

    # test search empty query
    def test_empty_query(self):
        response = self.client.get(
            f"{reverse('substitut:search')}?query=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context["products"]),
            len(Product.objects.all()))

    # test if the founded substitut has a better nutriscore
    def test_find_a_substitut(self):
        product = Product.objects.order_by('-nutriscore')[0]
        response = self.client.get(
            f"{reverse('substitut:find')}?product_id={product.pk}")
        self.assertLess(
            response.context['products'][0].nutriscore, product.nutriscore)

class TestProductPage(TestCase):
    fixtures = ['products']

    # test product page contains the required informations
    def test_product_page(self):
        product = Product.objects.all()[0]
        product_pk = product.pk
        response = self.client.get(
            f"{reverse('substitut:detail')}?product_id={product_pk}")
        self.assertContains(response, product.name)
        self.assertContains(response, product.nutriscore)
        self.assertContains(response, product.link)
        for level in product.nutrient_levels:
            self.assertContains(response, level)


class TestFavories(TestCase):
    fixtures = ['products']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_info = {
            "username": "test_user",
            "email": "user@test.com",
            "password": "test_user_password",
            "first_name": "Paul"}
        cls.user = User.objects.create_user(**cls.user_info)
        cls.product = Product.objects.all()[0]

    def setUp(self):
        self.client.login(
            username=self.user.username, password=self.user_info["password"])

    # test a favory is saved
    def test_save_favory(self):
        product_pk = self.product.pk
        response = self.client.post(
            reverse("substitut:favories"), {"product_pk": product_pk})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product, self.user.profile.favories.all())

    # test a user can see his favories
    def test_see_favories(self):
        self.user.profile.favories.add(self.product)
        response = self.client.get(reverse("substitut:favories"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    # test an unlogged user can't see his favories
    def test_see_favories_unlogged_user(self):
        self.client.logout()
        response = self.client.get(reverse("substitut:favories"))
        self.assertTemplateUsed(
            response, "substitut_search/favories_unlogged.html")
