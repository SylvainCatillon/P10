from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.test import tag

from selenium import webdriver

from accounts.tests.utils import log_user_in

from ..models import Product

class TestFavoriesSelenium(StaticLiveServerTestCase):
    fixtures = ['products']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Firefox()
        cls.selenium.implicitly_wait(15)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    @tag('selenium')
    def test_save(self):
        user = log_user_in(self.selenium, self.live_server_url)
        product = Product.objects.order_by('-nutriscore')[0]
        # assert that the user has no favories saved
        self.assertEqual(len(user.profile.favories.all()), 0)
        find_url = f"{reverse('substitut:find')}?product_id={product.pk}"
        self.selenium.get(self.live_server_url+find_url)
        fav_url = reverse('substitut:favories')
        self.selenium.find_element_by_xpath(
            f"//form[@action='{fav_url}']/button[@type='submit']").click()
        # assert that the user has one favorie saved
        self.assertEqual(len(user.profile.favories.all()), 1)
