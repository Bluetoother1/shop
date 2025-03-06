from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/',
         views.remove_from_cart, name='remove_from_cart'),
    path('create-order/', views.create_order, name='create_order'),
    path('payment-history', views.order_history, name='history'),
    path('repeat-order/<int:order_id>/',
         views.repeat_order, name='repeat_order'),
    path('payment-success/', views.payment_success, name='payment_success'),
]
