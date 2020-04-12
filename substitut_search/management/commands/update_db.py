from django.core.management.base import BaseCommand, CommandError

from substitut_search.utils.fill_db import FillDB
from substitut_search.models import Product

class Command(BaseCommand):
    """Add the command to update the database by dowloading
    the products on OpenFoodFacts.org"""
    help = 'Update the products in the database'

    def handle(self, *args, **options):
        """Update the database by dowloading
        the products on OpenFoodFacts.org"""
        count = Product.objects.count()
        fill_db = FillDB(nb_products=int(count*1.3))
        fill_db.update_products()
        message = f'Successfully updated the database'
        self.stdout.write(self.style.SUCCESS(message))
