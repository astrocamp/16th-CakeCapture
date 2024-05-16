from django.shortcuts import render, redirect
from .forms import OrderForm
from cart.cart import Cart
from .models import OrderMethod,Order,OrderItem
from django.contrib import messages
from django.contrib.auth.models import User


def order_form(request):
    form = OrderForm()
    return render(request, 'order/order_form.html', {'form': form})

def order_success(request):
    return render(request,'order/order_success.html')

def order_confirm(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            cart = Cart(request)
            cart_products = cart.get_prods
            quantities = cart.get_quants
            totals = cart.cart_total()
            my_shipping = request.POST
            request.session['my_shipping'] = my_shipping
            order_form = OrderForm(request.POST or None)
            return render(request,'order/order_confirm.html',{'cart_products':cart_products,'quantities':quantities,'totals':totals,'order_form':order_form})
            
        else:
            messages.error(request, '請檢查輸入的資料。')
            form = OrderForm()
            return redirect('order_form')

def order_process(request):
    if request.POST:
        my_shipping =request.session.get('my_shipping')
        user = request.user
        full_name= my_shipping['order_name']
        email= my_shipping['order_email']
        shipping_address = my_shipping['store_address']
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        amount_paid= totals
        #create order
        create_order = Order(user=user,full_name=full_name,email=email,
        shipping_address=shipping_address,amount_paid=amount_paid)
        create_order.save()
        return redirect('home')
    else:        
        return redirect('home')

    