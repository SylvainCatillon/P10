from django.test import TestCase

from ..models import Product


def create_product():
    """Create a product for testing purpose"""
    product_info = {
        "code": "2159404",
        "nutriscore": "a",
        "categories": ["en:test"],
        "name": "test1",
        "image": "https//image_test.com",
        "link": "https//test.com",
        "nutrient_levels": [
            'Matières grasses en quantitée faible (0g)',
            'Acides gras saturés en quantitée faible (0g)',
            'Sucres en quantitée faible (0g)',
            'Sel en quantitée faible (0.02794g)']
        }
    return Product.objects.create(**product_info)


class ProfileCreation(TestCase):
    """Test the model Product"""

    def test_product_creation(self):
        """Test if a product is created"""
        product = create_product()
        self.assertIsInstance(product, Product)
        self.assertEqual(product.__str__(), product.name)
