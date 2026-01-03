from django.urls import path
from . import views

urlpatterns = [
    path('', views.metal_rate, name='metal_rate'),
]
