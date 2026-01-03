"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

from backend import docs

urlpatterns = [
    # API Documentation
    path('docs/', docs.swagger_ui, name='swagger-ui'),
    path('openapi.json', docs.openapi_json, name='openapi-json'),
    
    # Legacy routes (DEPRECATED - for backward compatibility)
    # These endpoints are deprecated and will be removed in a future version
    # See API_MIGRATION_GUIDE.md for migration instructions
    path('', include('backend.api.v1.test.urls')),  # Root endpoints (ping, /users/, etc.)
    path('master-db/', include('backend.api.v1.test.urls')),  # Master DB operations
]
