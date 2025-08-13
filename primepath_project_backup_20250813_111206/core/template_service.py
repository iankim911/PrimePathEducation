"""
Template Service - Phase 7
Manages template rendering, component system, and caching
"""
from django.template.loader import render_to_string
from django.core.cache import cache
from django.conf import settings
from typing import Dict, Any, Optional, List
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for managing templates and components."""
    
    # Cache settings
    CACHE_PREFIX = 'template:'
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def render_component(cls, component_path: str, context: Dict[str, Any], 
                        use_cache: bool = True) -> str:
        """
        Render a template component with optional caching.
        
        Args:
            component_path: Path to component template
            context: Context data for rendering
            use_cache: Whether to use cache
            
        Returns:
            Rendered HTML string
        """
        if use_cache:
            cache_key = cls._get_cache_key(component_path, context)
            cached = cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for component: {component_path}")
                return cached
        
        try:
            rendered = render_to_string(component_path, context)
            
            if use_cache:
                cache.set(cache_key, rendered, cls.CACHE_TIMEOUT)
                
            return rendered
            
        except Exception as e:
            logger.error(f"Error rendering component {component_path}: {e}")
            return ""
    
    @classmethod
    def _get_cache_key(cls, component_path: str, context: Dict[str, Any]) -> str:
        """Generate cache key for component."""
        # Create hash from component path and context
        context_str = json.dumps(
            {k: str(v) for k, v in context.items() if k not in ['request', 'csrf_token']},
            sort_keys=True
        )
        hash_str = hashlib.md5(f"{component_path}:{context_str}".encode()).hexdigest()
        return f"{cls.CACHE_PREFIX}{hash_str}"
    
    @classmethod
    def get_component_context(cls, component_type: str, **kwargs) -> Dict[str, Any]:
        """
        Get standardized context for a component type.
        
        Args:
            component_type: Type of component (pdf_viewer, audio_player, etc.)
            **kwargs: Additional context data
            
        Returns:
            Standardized context dictionary
        """
        base_context = {
            'component_id': f"{component_type}_{kwargs.get('id', 'default')}",
            'component_class': f"component-{component_type}",
        }
        
        # Component-specific contexts
        if component_type == 'pdf_viewer':
            base_context.update({
                'pdf_url': kwargs.get('pdf_url', ''),
                'initial_page': kwargs.get('initial_page', 1),
                'allow_download': kwargs.get('allow_download', False),
                'show_controls': kwargs.get('show_controls', True),
            })
        
        elif component_type == 'audio_player':
            base_context.update({
                'audio_url': kwargs.get('audio_url', ''),
                'audio_name': kwargs.get('audio_name', 'Audio'),
                'autoplay': kwargs.get('autoplay', False),
                'show_progress': kwargs.get('show_progress', True),
            })
        
        elif component_type == 'timer':
            base_context.update({
                'duration_minutes': kwargs.get('duration_minutes', 60),
                'warning_minutes': kwargs.get('warning_minutes', 10),
                'auto_submit': kwargs.get('auto_submit', True),
                'show_seconds': kwargs.get('show_seconds', True),
            })
        
        elif component_type == 'question_nav':
            base_context.update({
                'total_questions': kwargs.get('total_questions', 0),
                'current_question': kwargs.get('current_question', 1),
                'answered_questions': kwargs.get('answered_questions', []),
                'show_status': kwargs.get('show_status', True),
            })
        
        base_context.update(kwargs)
        return base_context
    
    @classmethod
    def render_page_components(cls, page_type: str, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Render all components for a specific page type.
        
        Args:
            page_type: Type of page (student_test, exam_preview, etc.)
            context: Page context data
            
        Returns:
            Dictionary of rendered components
        """
        components = {}
        
        if page_type == 'student_test':
            # Render all student test components
            if context.get('exam', {}).get('pdf_file'):
                components['pdf_viewer'] = cls.render_component(
                    'components/placement_test/pdf_viewer.html',
                    cls.get_component_context(
                        'pdf_viewer',
                        pdf_url=context['exam']['pdf_file'],
                        exam_id=context['exam'].get('id')
                    )
                )
            
            if context.get('timer_minutes'):
                components['timer'] = cls.render_component(
                    'components/placement_test/timer.html',
                    cls.get_component_context(
                        'timer',
                        duration_minutes=context['timer_minutes'],
                        session_id=context.get('session', {}).get('id')
                    )
                )
            
            if context.get('audio_files'):
                components['audio_player'] = cls.render_component(
                    'components/placement_test/audio_player.html',
                    cls.get_component_context(
                        'audio_player',
                        audio_files=context['audio_files']
                    )
                )
            
            if context.get('total_questions'):
                components['question_nav'] = cls.render_component(
                    'components/placement_test/question_nav.html',
                    cls.get_component_context(
                        'question_nav',
                        total_questions=context['total_questions'],
                        current_question=context.get('current_question', 1)
                    )
                )
        
        elif page_type == 'exam_preview':
            # Render exam preview components
            if context.get('pdf_url'):
                components['pdf_viewer'] = cls.render_component(
                    'components/pdf/viewer.html',
                    cls.get_component_context(
                        'pdf_viewer',
                        pdf_url=context['pdf_url'],
                        allow_download=True
                    )
                )
        
        return components
    
    @classmethod
    def get_template_inheritance_chain(cls, template_name: str) -> List[str]:
        """
        Get the inheritance chain for a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            List of template names in inheritance order
        """
        chain = []
        
        # Define template inheritance patterns
        inheritance_map = {
            'placement_test/': ['placement_test/base.html', 'base.html'],
            'core/': ['core/base.html', 'base.html'],
            'components/': ['components/base.html'],
        }
        
        for prefix, parents in inheritance_map.items():
            if template_name.startswith(prefix):
                chain.extend(parents)
                break
        else:
            chain.append('base.html')
        
        chain.insert(0, template_name)
        return chain
    
    @classmethod
    def clear_template_cache(cls, pattern: Optional[str] = None):
        """
        Clear template cache.
        
        Args:
            pattern: Optional pattern to match cache keys
        """
        if hasattr(cache, 'delete_pattern'):
            if pattern:
                cache.delete_pattern(f"{cls.CACHE_PREFIX}*{pattern}*")
            else:
                cache.delete_pattern(f"{cls.CACHE_PREFIX}*")
            
            logger.info(f"Cleared template cache: {pattern or 'all'}")
        else:
            logger.warning("Cache backend doesn't support pattern deletion")
    
    @classmethod
    def preload_common_components(cls):
        """Preload commonly used components into cache."""
        common_components = [
            ('components/placement_test/timer.html', {'duration_minutes': 60}),
            ('components/placement_test/question_nav.html', {'total_questions': 20}),
            ('components/pdf/viewer.html', {'pdf_url': ''}),
        ]
        
        for component_path, context in common_components:
            try:
                cls.render_component(component_path, context, use_cache=True)
                logger.debug(f"Preloaded component: {component_path}")
            except Exception as e:
                logger.warning(f"Could not preload {component_path}: {e}")


class AssetBundlingService:
    """Service for managing frontend asset bundling and optimization."""
    
    @staticmethod
    def get_page_assets(page_type: str) -> Dict[str, List[str]]:
        """
        Get CSS and JS assets for a specific page type.
        
        Args:
            page_type: Type of page
            
        Returns:
            Dictionary with 'css' and 'js' lists
        """
        # Base assets for all pages
        base_assets = {
            'css': [
                'css/base.css',
                'css/bootstrap.min.css',
            ],
            'js': [
                'js/jquery.min.js',
                'js/bootstrap.bundle.min.js',
            ]
        }
        
        # Page-specific assets
        page_assets = {
            'student_test': {
                'css': [
                    'css/student_test.css',
                    'css/components/pdf_viewer.css',
                    'css/components/timer.css',
                    'css/components/audio_player.css',
                ],
                'js': [
                    'js/pdfjs/pdf.min.js',
                    'js/modules/timer.js',
                    'js/modules/audio-player.js',
                    'js/modules/answer-manager.js',
                    'js/modules/navigation.js',
                    'js/modules/memory-manager.js',
                    'js/modules/error-handler.js',
                ]
            },
            'exam_preview': {
                'css': [
                    'css/exam_preview.css',
                    'css/components/pdf_viewer.css',
                ],
                'js': [
                    'js/pdfjs/pdf.min.js',
                    'js/modules/pdf-viewer.js',
                ]
            },
            'teacher_dashboard': {
                'css': [
                    'css/dashboard.css',
                    'css/charts.css',
                ],
                'js': [
                    'js/chart.min.js',
                    'js/dashboard.js',
                ]
            },
            'exam_create': {
                'css': [
                    'css/exam_form.css',
                ],
                'js': [
                    'js/exam_form.js',
                    'js/file_upload.js',
                ]
            }
        }
        
        # Merge base and page-specific assets
        assets = base_assets.copy()
        if page_type in page_assets:
            assets['css'].extend(page_assets[page_type].get('css', []))
            assets['js'].extend(page_assets[page_type].get('js', []))
        
        return assets
    
    @staticmethod
    def get_bundle_url(asset_type: str, page_type: str) -> str:
        """
        Get bundled asset URL for production.
        
        Args:
            asset_type: 'css' or 'js'
            page_type: Type of page
            
        Returns:
            URL to bundled asset
        """
        if settings.DEBUG:
            # In development, return individual files
            return None
        
        # In production, return bundled file
        return f"/static/bundles/{page_type}.{asset_type}"
    
    @staticmethod
    def should_defer_script(script_path: str) -> bool:
        """Check if a script should be deferred."""
        defer_scripts = [
            'modules/memory-manager.js',
            'modules/error-handler.js',
            'dashboard.js',
        ]
        
        return any(defer in script_path for defer in defer_scripts)
    
    @staticmethod
    def should_async_script(script_path: str) -> bool:
        """Check if a script should be loaded async."""
        async_scripts = [
            'chart.min.js',
            'pdf.min.js',
        ]
        
        return any(async_script in script_path for async_script in async_scripts)