from django.shortcuts import render,redirect,get_object_or_404
import requests
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from cart.views import _cart_id
from cart.models import Cart,CartItem
from orders.models import Order,OrderProduct
from django.http import HttpResponse
# Verification Email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name,
                                               last_name=last_name,
                                               email=email,
                                               username=username,
                                               password=password)
            user.phone_number = phone_number
            user.save()

            # Create User Profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default.png'
            profile.save()

#===================== Sending Token to activate user account on email  ============================================

            current_site = get_current_site(request)  # Getting Current Domain Name
            mail_subject = "ShopyCart - Activate Your Account"
            message = render_to_string('accounts/verification_link.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_mail = email
            send_mail = EmailMessage(mail_subject,message,to=[to_mail])
            send_mail.send()
#=============================================================================================================

            # messages.success(request,"Thank you for registering with us. We have sent a verification mail.Kindly verify the mail. Thanks")

            return redirect('/accounts/login/?command=verify&email='+email)
    else:
        form = RegistrationForm
    context={
        'form':form,
    }
    return render(request,'accounts/register.html',context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)

        if user is not None:
            try: # This try block is used if there is item in cart without login then after login the cart items automatically assign to the user.
                cart = Cart.objects.get(cart_id = _cart_id(request))  # We request cart id before sign in
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()  # we check is item exists in cart before sign in
                if is_cart_item_exists:  # If yes
                    cart_item = CartItem.objects.filter(cart=cart) # Then we fetch the cart items
                    # Getting the product variation using cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get Cart items for user to access product variations
                    cart_item = CartItem.objects.filter(user=user)  # If cart exists then we get products in cart
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
#=================== Now Again Check if production_variation already exists in ex_var_list =============================================
                    for j in product_variation:
                        if j in ex_var_list:
                            index = ex_var_list.index(j)  # Getting Index of that item if variation exists
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.user = user   # Assign the item to the logged in user
                            item.quantity += 1  # Increase the Item having same variation in cart
                            item.save()   # Save Item

                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:   # Loop through all the items
                                item.user = user   # Assign all items to the user who logged in
                                item.save()   # Save Item with the logged in user

            except:
                pass
            auth.login(request,user)
            messages.success(request,"You are successfully logged in.")

# Here we basically do if user add some items in cart and then login we redirect it to checkout, in previous we are redirected to checkout
# But Now if there is next keyword then we redirect it to checkout page instead of dashboard
            url = request.META.get('HTTP_REFERER')   #  Getting Previous Page URL
            try:
                query = requests.utils.urlparse(url).query   # Store Previous page url in this case when we login ?next= (This url save) when we redirect to dashboard
                # ?next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))  # It splits where Equal Sign exists  # {'next': '/cart/checkout/'}
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)  # Now we redirect to checkout page
            except:
                return redirect('dashboard')
        else:
            messages.warning(request,'Invalid Credentials.Please Try Again!!')
            return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request,"You Are Suceessfully Logout")
    return redirect('login')


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,"Your Account is Activated")
        return redirect('login')
    else:
        messages.warning(request,'Invalid Verification Link')
        return redirect('register')

@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.order_by("-created_at").filter(user_id=request.user.id,is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user_id = request.user.id)
    context = {
        'orders_count':orders_count,
        'userprofile':userprofile
    }
    return render(request,'accounts/dashboard.html',context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            #====== Forgot Password Mail with token =====================
            current_site = get_current_site(request)  # Getting Current Domain Name
            mail_subject = "ShopyCart - Reset Password"
            message = render_to_string('accounts/reset_password.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_mail = email
            send_mail = EmailMessage(mail_subject,message,to=[to_mail])
            send_mail.send()

            messages.success(request,'Password Reset Link Sent To Your Mail.')
            return redirect('login')

        else:
            messages.warning(request,"Account Doesn't Exist.")
            return redirect('forgotPassword')

    return render(request,'accounts/forgotPassword.html')


def reset_password_validate(request,uidb64,token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid    # Save id of user in session after decode
        messages.info(request,'Please Reset Your Password')
        return redirect('resetPassword')

    else:
        messages.warning(request,'Link Expired !')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')  # Use id of user from session we store in upper view
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password Reset Successfully.')
            return redirect('login')

        else:
            messages.success(request,'Password Not Match')

    else:
        return render(request,'accounts/reset_password_after_validate.html')


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders,
    }
    return render(request,'accounts/my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user)
    if request.method == "POST":
        user_form = UserAccountForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Your Profile is successfully Updated.")
            return redirect('edit_profile')

    else:
        user_form = UserAccountForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
            'user_form':user_form,
            'profile_form':profile_form,
            'userprofile':userprofile
        }
    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        re_password = request.POST['re_password']

        user = Account.objects.get(username__exact= request.user.username)
        if new_password == re_password:
            success = user.check_password(current_password)  # check_password inbuilt django function to chech encryp password
            if success:
                user.set_password(new_password) # set_password inbuilt django function to store in form of encrypt password
                user.save()
                messages.success(request,'Password Updated Successfully')
                return redirect('change_password')
            else:
                messages.warning(request,"Please Enter Valid Current Password")

        else:
            messages.warning(request,"Passwords Doesn't Match")
            return redirect('change_password')
    return render(request,'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    sub_total = 0
    for i in order_detail:
        sub_total += i.product_price * i.quantity
    context = {
        'order_detail':order_detail,
        'order':order,
        'sub_total':sub_total
    }
    return render(request,'accounts/order_detail.html',context)