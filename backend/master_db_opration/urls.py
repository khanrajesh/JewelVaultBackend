from django.urls import path

from backend.master_db_opration.views import create_master_tables

urlpatterns = [
    path('create-tables/', create_master_tables, name='create-master-tables'),
]
