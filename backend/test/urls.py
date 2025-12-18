from django.urls import path

from backend.test.views import (
    list_users,
    list_vault_samples,
    ping_view,
    root_message,
    seed_vault_samples,
)

urlpatterns = [
    path('', root_message, name='root'),
    path('ping/', ping_view, name='ping'),
    path('users/', list_users, name='users'),
    path('vault-samples/', list_vault_samples, name='vault-samples'),
    path('vault-samples/seed/', seed_vault_samples, name='vault-samples-seed'),
]
