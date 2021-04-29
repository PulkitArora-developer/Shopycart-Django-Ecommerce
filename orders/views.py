from django.shortcuts import render,redirect
from django.http import HttpResponse
import razorpay
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import json
from django.views.decorators.csrf import csrf_exempt
from .forms import OrderForm
import datetime
from .models import *
from cart.models import CartItem
from shop.models import Product

def payments(request):
    return render(request,'orders/payments.html')


def place_order(request,total=0,quantity=0):
    current_user = request.user

    # If the cart Count <= 0 then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.products.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2*total)/100
    grand_total = total + tax
    razorpay_amount = grand_total*100

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store All Billing Info inside Order Table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.zip_code = form.cleaned_data['zip_code']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip_address = request.META.get('REMOTE_ADDR') # Take user ip address
            data.save()

            # Order No Generation (Unique)
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") # 20210505

            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # Getting Order Instance for Payment Gateway
            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            order_currency = 'INR'

            client = razorpay.Client(auth=('rzp_test_IlWmFu63lxusiQ', 'ir5w1PfJsNxML7smxJ36Bjpu'))
            payment = client.order.create({'amount': razorpay_amount, 'currency': order_currency, 'payment_capture': '1'})

            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
                'razorpay_amount':razorpay_amount
            }
            #=============================================
            return render(request,'orders/payments.html',context)
        else:
            # print(form.errors)
            return redirect('checkout')
    else:
        return redirect('checkout')


@csrf_exempt
def success(request,order_number):
    try:
        current_user = request.user
        order = Order.objects.get(user=current_user, order_number=order_number)
        order.is_ordered = True
        order.save()

        # Move the Cart Items to OrderProduct table
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order_id = order.id
            order_product.user_id = request.user.id
            order_product.product_id = item.products_id
            order_product.quantity = item.quantity
            order_product.product_price = item.products.price
            order_product.ordered = True
            order_product.save()

            # Now save the product variations
            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variation)
            order_product.save()


            # Reduce the quantity from inventory (Stock)
            product = Product.objects.get(id=item.products_id)
            product.stock -= item.quantity
            product.save()


        # Clear the Cart
        CartItem.objects.filter(user=request.user).delete()


        # Send Order Mail to Customer
        mail_subject = "Thank You For Shopping With Us-ShopyCart"
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order':order,
        })
        to_mail = request.user.email
        send_mail = EmailMessage(mail_subject, message, to=[to_mail])
        send_mail.send()

        #================== Thank You Page ==================
        order_details = Order.objects.get(user=request.user, order_number=order_number,is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id = order_details.id)
        sub_total = 0
        for i in order_products:
            sub_total += i.product_price * i.quantity

        context = {
            'order_products':order_products,
            'order':order_details,
            'user':request.user,
            'sub_total':sub_total
        }
        return render(request, 'orders/order_complete.html',context)


    except(Order.DoesNotExist):
        return redirect('index')


