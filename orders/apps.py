from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        # Import signals here so it runs after apps are loaded
        import orders.signals  # noqa: F401
