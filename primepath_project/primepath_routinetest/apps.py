from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class PrimepathRoutinetestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'primepath_routinetest'
    verbose_name = 'PrimePath Routine Test'
    
    def ready(self):
        """
        Called when Django starts. Import template tags to ensure they're registered.
        """
        logger.info("[ROUTINETEST_APP] App ready method called")
        print("[ROUTINETEST_APP] App ready method called")
        
        # Import template tags to ensure they're registered
        try:
            from primepath_routinetest.templatetags import matrix_filters, routinetest_grade_tags
            logger.info("[ROUTINETEST_APP] Template tags imported in ready()")
            print("[ROUTINETEST_APP] Template tags imported in ready()")
        except ImportError as e:
            logger.error(f"[ROUTINETEST_APP] Error importing template tags in ready(): {e}")
            print(f"[ROUTINETEST_APP] Error importing template tags in ready(): {e}")
        
        # Import signal handlers if any
        try:
            from . import signals
            logger.info("[ROUTINETEST_APP] Signals imported")
        except ImportError:
            pass  # No signals defined yet