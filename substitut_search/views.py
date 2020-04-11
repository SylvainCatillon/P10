from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden

from .models import Product

NB_DISPLAYED_PRODUCTS = 12

def search(request):
    """
    Takes a request GET with a query
    Displays products whose names contains the query
    Displays 12 random products if the query is empty

    Template: "substitut_search/search.html"
    Context: {"products": a list of products, "query": the initial query}
    """
    query = request.GET.get("query")
    if not query:
        query = "Produits aléatoires"
        products = Product.objects.order_by('?')[:NB_DISPLAYED_PRODUCTS]
    else:
        #  Fetch the products whose names starts with the query
        products = list(
            Product.objects.filter(name__istartswith=query)
            [:NB_DISPLAYED_PRODUCTS])
        #  If there is not enough products,
        #  add the products whose names contains the query
        len_products = len(products)
        if len_products < NB_DISPLAYED_PRODUCTS:
            products2 = Product.objects.exclude(name__istartswith=query)
            #  Split the query to search the words separately
            for word in query.split():
                products2 = products2.filter(name__icontains=word)
            products += list(products2[:NB_DISPLAYED_PRODUCTS-len_products])

    context = {"products": products, "query": query}
    return render(request, "substitut_search/search.html", context)

def find(request):
    """
    Takes a request GET with a product pk
    Displays substituts to the initial product

    Template: "substitut_search/find.html"
    Context: {
        "initial_product": the product in the initial search,
        "products": a list of the products found as substituts}
    """
    product_pk = request.GET.get("product_id")
    product = get_object_or_404(Product, pk=product_pk)
    substituts = []
    max_sbts = NB_DISPLAYED_PRODUCTS
    #  search in categories, starting from the smaller
    #  until enough substituts are found
    for category in reversed(product.categories):
        #  find the products in the category with a better nutriscore
        cat_sbts = Product.objects \
                          .filter(categories__contains=[category]) \
                          .filter(nutriscore__lt=product.nutriscore) \
                          .order_by('nutriscore')
        #  add the products in the result list, without exceed the max
        substituts += cat_sbts[:max_sbts-len(substituts)]
        #  if the result list have enough products, end the search
        if len(substituts) >= max_sbts:
            break
    context = {
        "initial_product": product,
        "products": substituts
        }
    return render(request, "substitut_search/find.html", context)

def detail(request):
    """
    Takes a request GET with a product pk
    Displays the informations of the product

    Template: "substitut_search/detail.html"
    Context: {"product": the searched product}
    """
    product_pk = request.GET.get("product_id")
    product = get_object_or_404(Product, pk=product_pk)
    return render(request, "substitut_search/detail.html", {"product": product})

def favories(request):
    """
    Takes a request GET or POST with a product pk
    If the method is POST, save the product in the user favories
    Else, displays the saved products of the user

    Template: "substitut_search/favories.html"
    Context: {"products": a list of the products saved by the user}
    """
    user = request.user
    #  a user need to be authenticated to access this page
    if not user.is_authenticated:
        return render(request, "substitut_search/favories_unlogged.html")
    #  if the request method is POST, save the product in the user favories
    if request.method == "POST":
        product_pk = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_pk)
        user.profile.favories.add(product)
        #  return an HttpResponse which will be displayed by a jquerry script
        return HttpResponse("Produit sauvegardé")
    #  if the method isn't POST, display the saved products of the user
    products = user.profile.favories.all()
    return render(
        request, "substitut_search/favories.html", {'products': products})
