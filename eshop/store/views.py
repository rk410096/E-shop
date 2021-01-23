from django.shortcuts import render, redirect
from django.http import HttpResponse
from store.models import *
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.views import View

# Create your views here.


class Index(View):
    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity<=1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1
                
            else:
                 cart[product] = 1
        else:
             cart = {}
             cart[product] = 1
        
        request.session['cart'] = cart
        print('cart', request.session['cart'])
        return redirect('homepage')

    def get(self, request):
        cart = request.session.get('cart')
        if not cart:
            request.session['cart']={}
        products = None
        categories = Category.get_all_categories()
        categoryID = request.GET.get('category')
        if categoryID:
            products = Product.get_all_products_by_categoryid(categoryID)
        else:
            products = Product.get_all_products()
        data = {}
        data['products'] = products
        data['categories'] = categories
        print('you are :', request.session.get('email'))
        return render(request, 'index.html', data)


def validateCustomer(customer):
    error_message = None
    if(not customer.first_name):
        error_message = "First Name Required!!"
    elif len(customer.first_name) < 4:
        error_message = "First name must be min 4 char"
    elif not customer.last_name:
        error_message = "last Name Required!!"
    elif len(customer.last_name) < 4:
        error_message = "last name must be min 4 char"
    elif not customer.mobile:
        error_message = "Mobile No. is required"
    elif len(customer.mobile) < 10:
        error_message = "Mobile No. is must be 10 digit"
    elif len(customer.email) < 5:
        error_message = "email is must be 5 character"
    elif len(customer.password) < 6:
        error_message = "password is must be 6 character"
    elif customer.isExists():
        error_message = 'Email address is already registerd'
    return error_message


def registerUser(request):
    postData = request.POST
    first_name = postData.get('first_name')
    last_name = postData.get('last_name')
    mobile = postData.get('mobile')
    email = postData.get('email')
    password = postData.get('password')
    # Validation
    value = {
        'first_name': first_name,
        'last_name': last_name,
        'mobile': mobile,
        'email': email,
    }
    error_message = None

    customer = Customer(first_name=first_name,
                        last_name=last_name,
                        mobile=mobile,
                        email=email,
                        password=password)

    error_message = validateCustomer(customer)
    # saving
    if not error_message:
        print(first_name, last_name, mobile, email, password)
        customer.password = make_password(customer.password)
        customer.register()
        return redirect('homepage')
    else:
        data = {
            'error': error_message,
            'values': value
        }
        return render(request, 'signup.html', data)


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    else:
        return registerUser(request)


class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id
                # save session object
                #request.session['email'] = customer.email
                return redirect('homepage')
            else:
                error_message = 'Email or Password is Invalid'
        else:
            error_message = 'Email or Password is Invalid'
        print(email, password)
        return render(request, 'login.html', {'error': error_message})

def logout(request):
    request.session.clear()
    return redirect('login')

class Cart(View):
    def get(self, request):
        ids = list(request.session.get('cart').keys())
        products = Product.get_products_by_id(ids)
        print(products)
        return render(request, 'cart.html', {'products' : products})

class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))
        print(address, mobile, customer, cart, products)

        for product in products:
            order = Order(customer = Customer(id = customer),
                        product = product,
                        price = product.price,
                        address = address,
                        mobile = mobile,
                        quantity = cart.get(str(product.id)))
            
            order.save()
            request.session['cart'] = {}

        return redirect('cart')

class OrderView(View):
    def get(self, request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(orders)
        return render(request, 'orders.html', {'orders':orders})
