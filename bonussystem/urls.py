from django.urls import path
from . import views

urlpatterns = [
    path('', views.bonus_history, name='bonus'),

]
