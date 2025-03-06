from django.shortcuts import render, get_object_or_404
from .models import Product, Category
# Create your views here.


def shop(request):
    products = Product.objects.all()
    categores = Category.objects.all()
    return render(request, 'shop/shop.html', {'products': products, 'categores': categores})


def one_category(request, category_id):

    category = get_object_or_404(Category, pk=category_id)
    products = category.product_set.all()
    return render(request, 'shop/one_category.html', {'category': category, 'products': products})
