# primepath_routinetest app initialization
import logging

logger = logging.getLogger(__name__)

# Set default app config
default_app_config = 'primepath_routinetest.apps.PrimepathRoutinetestConfig'

# Force import of templatetags to ensure they're registered
try:
    from . import templatetags
    logger.info("[ROUTINETEST] Template tags imported successfully")
    print("[ROUTINETEST] Template tags imported successfully")
except ImportError as e:
    logger.warning(f"[ROUTINETEST] Could not import templatetags: {e}")
    print(f"[ROUTINETEST] Could not import templatetags: {e}")

logger.info("[ROUTINETEST] App initialized")
print("[ROUTINETEST] App initialized")