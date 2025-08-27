from django.apps import AppConfig


class PlacementTestConfig(AppConfig):

    def ready(self):
        """Initialize services when app is ready."""
        from core.service_registry import initialize_services
        try:
            initialize_services()
        except Exception:
            pass  # Services may already be initialized

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'placement_test'