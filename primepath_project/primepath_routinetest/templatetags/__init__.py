# Template tags module for primepath_routinetest
# Contains custom template filters for the app

# Import all template tag modules to ensure they're registered
import logging

logger = logging.getLogger(__name__)

try:
    from . import grade_tags
    from . import matrix_filters
    logger.info("[TEMPLATETAGS] Successfully imported grade_tags and matrix_filters")
    print("[TEMPLATETAGS] Successfully imported grade_tags and matrix_filters")
except ImportError as e:
    logger.error(f"[TEMPLATETAGS] Error importing template tags: {e}")
    print(f"[TEMPLATETAGS] Error importing template tags: {e}")

# Force Django to recognize this as a template tags package
__all__ = ['grade_tags', 'matrix_filters']