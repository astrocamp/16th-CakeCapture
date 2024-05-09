from django.shortcuts import render


def home(request):
    return render(request, "pages/home.html")

def detail(request):
    return render(request, "products/item_detail.html")

def about(request):
    return render(request, "pages/about.html")

def cart_detail(request):
    return render(request, "cart/cart_detail.html")

def cart_list(request):
    return render(request, "pages/cart_list.html")

def cart_confirm(request):
    return render(request, "pages/cart_confirm")
