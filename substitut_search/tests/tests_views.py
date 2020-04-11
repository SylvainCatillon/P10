from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ..models import Product


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
            reverse("substitut:favories"), {"product_id": product_pk})
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
