from django.shortcuts import render
from django.http import HttpResponse

from shop.models import Product,ReviewRating

def index(request):
    query = Product.objects.all().filter(is_available=True).order_by('created_on')

    reviews = None
    for product in query:
        reviews = ReviewRating.objects.filter(product_id=product.id, status_flag=True)

    context = {
        'products':query,
        'reviews':reviews
    }
    return render(request,'index.html',context)
