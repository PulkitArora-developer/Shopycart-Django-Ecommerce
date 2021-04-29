from django.shortcuts import render,get_object_or_404,redirect
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.contrib import messages
from django.db.models import Q
from orders.models import Order,OrderProduct
from cart.views import _cart_id
from .forms import *
from cart.models import Cart,CartItem
from .models import Product,ReviewRating,ProductGallery
from category.models import Category


def store(request,category_slug=None):
    categories = None
    products = None

    if category_slug:
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories).filter(is_available=True).all().order_by('id')
        paginator = Paginator(products,6)  # We want 6 Products to show in a page
        page = request.GET.get('page')   # here 'page' refers in url ?page=2
        pagedProduct = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products,6)  # We want 6 Products to show in a page
        page = request.GET.get('page')   # here 'page' refers in url ?page=2
        pagedProduct = paginator.get_page(page)
        product_count = products.count()

    context = {
        'product':pagedProduct,
        'product_count':product_count,
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),products=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:  # Checking whether user purchase particular product for review
            orderproduct = OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None

    else:
        orderproduct=None

    # Get the reviews from all customers
    reviews = ReviewRating.objects.filter(product_id=single_product.id,status_flag=True)
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context={
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery
    }

    return render(request,'store/product_details.html',context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name=keyword)).order_by('-created_on')
            product_count = products.count()
    context = {
        'product':products,
        'product_count':product_count
    }
    return render(request, 'store/store.html',context)


def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form = ReviewForm(request.POST,instance=reviews) # If there is already a review then update that review otherwise save
            form.save()
            messages.success(request,'Thank You! Your Review is updated successfully.')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request,'Thanks Your Review is submitted.')
                return redirect(url)
