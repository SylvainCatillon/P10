from django.db import models
from django.contrib.postgres.fields import ArrayField

class Product(models.Model):
    """A product downloaded from OpenFoodFacts"""
    code = models.CharField(max_length=50, primary_key=True)
    ns_choices = [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D"), ("e", "E")]
    nutriscore = models.CharField(
        max_length=1, choices=ns_choices, db_index=True)
    categories = ArrayField(models.CharField(max_length=100))
    name = models.CharField(max_length=200, unique=True)
    image = models.URLField()
    link = models.URLField(unique=True)
    nutrient_levels = ArrayField(models.CharField(max_length=80), default=list)

    def __str__(self):
        return self.name

class Favory(models.Model):
    """Relation table between Product and User"""
    user_profile = models.ForeignKey(
        'accounts.Profile', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name
