from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .models import *
from shop.models import Product,Variation

def _cart_id(request):   # Private Function
    cart = request.session.session_key    # Here we request session i.e is cart already exist in the session
    if not cart:
        cart = request.session.create()  # If no then we create using the particular session at that time
    return cart

def add_to_cart(request,product_id):
    # Getting Current User
    current_user = request.user

    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:  # Check whether the current user is authenticated or not
        product_variation = []
        # color = request.GET['color']
        # size = request.GET['size']
        # return HttpResponse(color+" "+ size)
        if request.method == 'POST':
            # color = request.POST['color']
            # size = request.POST['size']
            for item in request.POST:
                key = item
                value = request.POST[key]
                # Taking POST values dynamically so in the future if we add more variation then there is no error
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        is_cart_item_exists = CartItem.objects.filter(products=product,user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(products=product,user=current_user)  # If cart exists then we get products in cart
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # Increase Cart Item QTY
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(products=product,id=item_id)
                item.quantity += 1
                item.save()
            else:
                # Create a new Cart Item
                item = CartItem.objects.create(products=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()    # Save Cart Items if there is changes

        else:   # If there is no product in cart
            cart_item = CartItem.objects.create(   # We simply add one product by 1 using product_id and cart_id using session
                products = product,
                user = current_user,
                quantity = 1
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')
    # If the user is not authenticated ==================================

    else:
        product_variation = []
        # color = request.GET['color']
        # size = request.GET['size']
        # return HttpResponse(color+" "+ size)
        if request.method == 'POST':
            # color = request.POST['color']
            # size = request.POST['size']
            for item in request.POST:
                key = item
                value = request.POST[key]
                # Taking POST values dynamically so in the future if we add more variation then there is no error
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))  # If there is already a cart then get using session key
        except Cart.DoesNotExist:
            cart = Cart.objects.create(     # If there is no cart then we create a new cart using the session key
                cart_id = _cart_id(request)
            )
        cart.save()         # Save the Cart

        is_cart_item_exists = CartItem.objects.filter(products=product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(products=product,cart=cart)  # If cart exists then we get products in cart
            # existing variation -> database
            # product_variation ->  list above
            # item id ->  database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # Increase Cart Item QTY
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(products=product,id=item_id)
                item.quantity += 1
                item.save()
            else:
                # Create a new Cart Item
                item = CartItem.objects.create(products=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()    # Save Cart Items if there is changes

        else:   # If there is no product in cart
            cart_item = CartItem.objects.create(   # We simply add one product by 1 using product_id and cart_id using session
                products = product,
                cart = cart,
                quantity = 1
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')


def remove_items_from_cart(request,product_id,cart_item_id):
    product = Product.objects.get(id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(products=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(products=product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_items_from_cart_all(request,product_id,cart_item_id):
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(products=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(products=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))  # Get Cart Session
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)  # Filter all Products using the cart (session)
        for items in cart_items:
            total += (items.products.price * items.quantity)  # Here we calculate total of eact product
            quantity += items.quantity  # Here we calculate each quantity of product

        tax = (2*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items':cart_items,
        'total':total,
        'quantity':quantity,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,'store/cart.html',context)

@login_required(login_url="login")
def checkout(request,total=0,quantity=0,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # Get Cart Session
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)  # Filter all Products using the cart (session)
        for items in cart_items:
            total += (items.products.price * items.quantity)  # Here we calculate total of eact product
            quantity += items.quantity  # Here we calculate each quantity of product

        tax = (2*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items':cart_items,
        'total':total,
        'quantity':quantity,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,'store/checkout.html',context)