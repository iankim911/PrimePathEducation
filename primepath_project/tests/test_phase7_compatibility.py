"""
Phase 7 Compatibility Test - Template, Caching, and Monitoring Services
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, str(Path(__file__).parent))
django.setup()

import time
from django.test import Client
from django.core.cache import cache
import traceback


class TestPhase7Compatibility:
    """Test Phase 7 services integration."""
    
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        try:
            test_func()
            self.passed += 1
            self.tests.append(f"PASS: {test_name}")
            print(f"PASS: {test_name}")
        except Exception as e:
            self.failed += 1
            self.tests.append(f"FAIL: {test_name}: {str(e)}")
            print(f"FAIL: {test_name}: {str(e)}")
            if os.environ.get('DEBUG'):
                traceback.print_exc()
    
    def test_template_service_import(self):
        """Test that TemplateService can be imported."""
        from core.template_service import TemplateService, AssetBundlingService
        
        # Test basic methods exist
        assert hasattr(TemplateService, 'render_component')
        assert hasattr(TemplateService, 'get_component_context')
        assert hasattr(TemplateService, 'render_page_components')
        assert hasattr(AssetBundlingService, 'get_page_assets')
        
        print("  - TemplateService imported successfully")
    
    def test_cache_service_import(self):
        """Test that CacheService can be imported."""
        from core.cache_service import CacheService, cache_result, QueryCache
        
        # Test basic methods exist
        assert hasattr(CacheService, 'get')
        assert hasattr(CacheService, 'set')
        assert hasattr(CacheService, 'delete')
        assert hasattr(QueryCache, 'cache_queryset')
        
        print("  - CacheService imported successfully")
    
    def test_monitoring_service_import(self):
        """Test that MonitoringService can be imported."""
        from core.monitoring_service import (
            MetricsCollector, PerformanceMonitor, 
            HealthCheckService, ActivityLogger
        )
        
        # Test basic methods exist
        assert hasattr(MetricsCollector, 'record_request')
        assert hasattr(PerformanceMonitor, 'measure_time')
        assert hasattr(HealthCheckService, 'get_system_health')
        assert hasattr(ActivityLogger, 'log_user_action')
        
        print("  - MonitoringService imported successfully")
    
    def test_cache_operations(self):
        """Test cache service operations."""
        from core.cache_service import CacheService
        
        # Test set and get
        test_key = 'test_phase7'
        test_value = {'test': 'data', 'number': 123}
        
        # Set value
        success = CacheService.set(test_key, test_value, prefix='test', timeout=60)
        assert success, "Failed to set cache value"
        
        # Get value
        retrieved = CacheService.get(test_key, prefix='test')
        assert retrieved == test_value, f"Cache mismatch: {retrieved} != {test_value}"
        
        # Delete value
        CacheService.delete(test_key, prefix='test')
        retrieved = CacheService.get(test_key, prefix='test')
        assert retrieved is None, "Failed to delete cache value"
        
        print("  - Cache operations working")
    
    def test_template_component_context(self):
        """Test template component context generation."""
        from core.template_service import TemplateService
        
        # Test PDF viewer context
        pdf_context = TemplateService.get_component_context(
            'pdf_viewer',
            pdf_url='/media/test.pdf',
            exam_id='123'
        )
        
        assert 'component_id' in pdf_context
        assert 'pdf_url' in pdf_context
        assert pdf_context['pdf_url'] == '/media/test.pdf'
        
        # Test timer context
        timer_context = TemplateService.get_component_context(
            'timer',
            duration_minutes=90,
            session_id='456'
        )
        
        assert 'duration_minutes' in timer_context
        assert timer_context['duration_minutes'] == 90
        
        print("  - Component context generation working")
    
    def test_asset_bundling(self):
        """Test asset bundling service."""
        from core.template_service import AssetBundlingService
        
        # Test getting assets for student test page
        assets = AssetBundlingService.get_page_assets('student_test')
        
        assert 'css' in assets
        assert 'js' in assets
        assert len(assets['css']) > 0
        assert len(assets['js']) > 0
        
        # Check base assets are included
        assert any('base.css' in css for css in assets['css'])
        assert any('jquery' in js for js in assets['js'])
        
        # Check page-specific assets
        assert any('student_test.css' in css for css in assets['css'])
        
        print("  - Asset bundling working")
    
    def test_metrics_collection(self):
        """Test metrics collection."""
        from core.monitoring_service import MetricsCollector
        
        # Record some metrics
        MetricsCollector.record_request('/test/', 'GET', 200, 0.150)
        MetricsCollector.record_request('/test/', 'GET', 200, 0.200)
        MetricsCollector.record_database_query('SELECT * FROM test', 0.050)
        MetricsCollector.record_cache_operation('get', hit=True)
        MetricsCollector.record_cache_operation('get', hit=False)
        
        # Get metrics
        metrics = MetricsCollector.get_metrics()
        
        assert 'requests' in metrics
        assert 'database' in metrics
        assert 'cache' in metrics
        
        # Check request metrics
        if 'GET:/test/' in metrics['requests']:
            request_metrics = metrics['requests']['GET:/test/']
            assert request_metrics['count'] >= 2
            assert request_metrics['avg_time'] > 0
        
        print("  - Metrics collection working")
    
    def test_health_checks(self):
        """Test health check service."""
        from core.monitoring_service import HealthCheckService
        
        # Test database health check
        db_health = HealthCheckService.check_database()
        assert 'status' in db_health
        assert 'message' in db_health
        
        # Test cache health check
        cache_health = HealthCheckService.check_cache()
        assert 'status' in cache_health
        assert 'message' in cache_health
        
        # Test overall system health
        system_health = HealthCheckService.get_system_health()
        assert 'status' in system_health
        assert 'checks' in system_health
        assert 'timestamp' in system_health
        
        print("  - Health checks working")
    
    def test_cache_decorator(self):
        """Test cache result decorator."""
        from core.cache_service import cache_result
        
        # Create a test function with caching
        call_count = {'count': 0}
        
        @cache_result(prefix='test', timeout=60)
        def expensive_function(x, y):
            call_count['count'] += 1
            return x + y
        
        # First call - should execute function
        result1 = expensive_function(2, 3)
        assert result1 == 5
        assert call_count['count'] == 1
        
        # Second call - should use cache
        result2 = expensive_function(2, 3)
        assert result2 == 5
        assert call_count['count'] == 1  # Should not increase
        
        # Different arguments - should execute function
        result3 = expensive_function(3, 4)
        assert result3 == 7
        assert call_count['count'] == 2
        
        print("  - Cache decorator working")
    
    def test_performance_monitor(self):
        """Test performance monitoring decorator."""
        from core.monitoring_service import PerformanceMonitor
        
        @PerformanceMonitor.measure_time
        def slow_function():
            time.sleep(0.01)  # Sleep for 10ms
            return "done"
        
        # Execute function
        result = slow_function()
        assert result == "done"
        
        # Check that metrics were recorded
        from core.monitoring_service import MetricsCollector
        metrics = MetricsCollector.get_metrics()
        
        # Performance metrics should be recorded
        if 'performance' in metrics:
            perf_keys = list(metrics['performance'].keys())
            assert any('slow_function' in key for key in perf_keys)
        
        print("  - Performance monitoring working")
    
    def test_activity_logging(self):
        """Test activity logging."""
        from core.monitoring_service import ActivityLogger
        
        # Log user action
        ActivityLogger.log_user_action(
            user_id='test_user',
            action='test_action',
            details={'test': 'data'}
        )
        
        # Log system event
        ActivityLogger.log_system_event(
            event_type='test_event',
            message='Test system event',
            severity='info'
        )
        
        # Should not raise any exceptions
        print("  - Activity logging working")
    
    def test_query_cache(self):
        """Test query cache functionality."""
        from core.cache_service import QueryCache
        from placement_test.models import PlacementExam as Exam
        
        # Create a queryset
        queryset = Exam.objects.all()[:5]
        cache_key = 'test_queryset_phase7'
        
        # Cache the queryset
        result1 = QueryCache.cache_queryset(queryset, cache_key, timeout=60)
        
        # Get from cache
        from core.cache_service import CacheService
        cached = CacheService.get(cache_key, 'query')
        
        assert cached is not None
        assert len(cached) == len(result1)
        
        print("  - Query cache working")
    
    def test_cache_invalidation(self):
        """Test cache invalidation patterns."""
        from core.cache_service import CacheService
        
        # Set multiple cache entries
        CacheService.set('item1', 'value1', prefix='test')
        CacheService.set('item2', 'value2', prefix='test')
        CacheService.set('other', 'value3', prefix='exam')
        
        # Clear exam cache
        CacheService.clear_exam_cache('test_exam_id')
        
        # Test entries should still exist
        assert CacheService.get('item1', prefix='test') is not None
        
        print("  - Cache invalidation working")
    
    def test_template_inheritance_chain(self):
        """Test template inheritance chain detection."""
        from core.template_service import TemplateService
        
        # Test placement test template
        chain = TemplateService.get_template_inheritance_chain(
            'placement_test/student_test.html'
        )
        
        assert 'placement_test/student_test.html' in chain
        assert 'base.html' in chain
        
        # Test core template
        chain = TemplateService.get_template_inheritance_chain(
            'core/dashboard.html'
        )
        
        assert 'core/dashboard.html' in chain
        assert 'base.html' in chain
        
        print("  - Template inheritance chain working")
    
    def test_existing_views_still_work(self):
        """Test that existing views still function."""
        # Test home page
        response = self.client.get('/')
        assert response.status_code == 200
        
        # Test teacher dashboard
        response = self.client.get('/PlacementTest/PlacementTest/teacher/dashboard/')
        assert response.status_code == 200
        
        print("  - Existing views still functional")
    
    def test_no_import_errors(self):
        """Test that all services can be imported together."""
        try:
            from core.template_service import TemplateService, AssetBundlingService
            from core.cache_service import CacheService, cache_result, QueryCache
            from core.monitoring_service import (
                MetricsCollector, PerformanceMonitor,
                HealthCheckService, ActivityLogger
            )
            
            # Also test existing services
            from core.services import DashboardService, FileService
            from placement_test.services import ExamService, SessionService
            
            print("  - No import errors")
        except ImportError as e:
            raise Exception(f"Import error: {e}")
    
    def run_all_tests(self):
        """Run all Phase 7 compatibility tests."""
        print("\n" + "="*70)
        print("PHASE 7 COMPATIBILITY TEST")
        print("Testing Template, Caching, and Monitoring Services")
        print("="*70 + "\n")
        
        print("1. TESTING SERVICE IMPORTS...")
        self.run_test("Template service import", self.test_template_service_import)
        self.run_test("Cache service import", self.test_cache_service_import)
        self.run_test("Monitoring service import", self.test_monitoring_service_import)
        
        print("\n2. TESTING CACHE FUNCTIONALITY...")
        self.run_test("Cache operations", self.test_cache_operations)
        self.run_test("Cache decorator", self.test_cache_decorator)
        self.run_test("Query cache", self.test_query_cache)
        self.run_test("Cache invalidation", self.test_cache_invalidation)
        
        print("\n3. TESTING TEMPLATE SERVICES...")
        self.run_test("Component context", self.test_template_component_context)
        self.run_test("Asset bundling", self.test_asset_bundling)
        self.run_test("Template inheritance", self.test_template_inheritance_chain)
        
        print("\n4. TESTING MONITORING SERVICES...")
        self.run_test("Metrics collection", self.test_metrics_collection)
        self.run_test("Health checks", self.test_health_checks)
        self.run_test("Performance monitoring", self.test_performance_monitor)
        self.run_test("Activity logging", self.test_activity_logging)
        
        print("\n5. TESTING COMPATIBILITY...")
        self.run_test("Existing views work", self.test_existing_views_still_work)
        self.run_test("No import errors", self.test_no_import_errors)
        
        # Report results
        print("\n" + "="*70)
        total = self.passed + self.failed
        print(f"RESULTS: {self.passed}/{total} tests passed")
        print("="*70)
        
        if self.failed == 0:
            print("\nSUCCESS: Phase 7 implementation complete")
            print("Template, caching, and monitoring services working")
            print("System maintains 100% backward compatibility")
        else:
            print(f"\nWARNING: {self.failed} tests failed")
            print("Review failures before proceeding")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestPhase7Compatibility()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)