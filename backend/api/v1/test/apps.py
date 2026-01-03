from django.apps import AppConfig


class TestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.api.v1.test'
    verbose_name = 'Test/Legacy API'
