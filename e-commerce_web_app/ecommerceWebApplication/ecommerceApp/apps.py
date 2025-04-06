from django.apps import AppConfig


class EcommerceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ecommerceApp'

    def ready(self):
        # Import signals module
        import ecommerceApp.signals