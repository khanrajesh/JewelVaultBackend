"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

from backend import docs

# Version prefix for API routes
v1 = "api/v1"

urlpatterns = [
    # API Documentation
    path(f'{v1}/docs/', docs.swagger_ui, name='swagger-ui'),
    path(f'{v1}/openapi.json', docs.openapi_json, name='openapi-json'),
    
    # API Routes
    path(f'{v1}/', include('backend.api.v1.metal_rate.urls')),


    path(f'{v1}/', include('backend.api.v1.test.urls')),  # Root endpoints (ping, /users/, etc.)
    path('master-db/', include('backend.api.v1.test.urls')),  # Master DB operations
]
