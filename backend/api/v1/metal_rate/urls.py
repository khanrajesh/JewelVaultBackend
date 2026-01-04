from django.urls import path
from . import views

urlpatterns = [
    path('metal-rate', views.metal_rate, name='metal_rate'),
]
