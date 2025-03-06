from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop, name='shop'),
    path('<int:category_id>', views.one_category, name='one_category'),
]
