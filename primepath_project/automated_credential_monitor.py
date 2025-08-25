"""
Automated Credential Monitoring System
=====================================

A comprehensive monitoring system that automatically detects, reports, and fixes
credential corruption issues before they impact production users.

Key Features:
1. Continuous credential validation monitoring
2. Automated detection of corruption events
3. Real-time alerting and notification system
4. Self-healing capabilities for critical accounts
5. Comprehensive audit trail and reporting
6. Integration with deployment pipelines

Author: Claude Code AI System
Date: August 25, 2025
"""
import os
import sys
import django
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.utils import timezone
from django.conf import settings
from user_credential_service import credential_service
from credential_protection_middleware import get_protection_report


logger = logging.getLogger(__name__)


@dataclass
class MonitoringAlert:
    """Represents a monitoring alert."""
    alert_id: str
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    account: str
    issue_type: str
    description: str
    timestamp: datetime
    resolved: bool = False
    resolution_action: Optional[str] = None
    resolution_timestamp: Optional[datetime] = None


class CredentialMonitor:
    """
    Automated monitoring system for user credentials.
    
    This system runs continuous checks to ensure credential integrity
    and can automatically fix issues when they are detected.
    """
    
    def __init__(self):
        self.service = credential_service
        self.monitoring_enabled = getattr(settings, 'CREDENTIAL_MONITORING_ENABLED', True)
        self.auto_fix_enabled = getattr(settings, 'CREDENTIAL_AUTO_FIX_ENABLED', True)
        self.check_interval = getattr(settings, 'CREDENTIAL_CHECK_INTERVAL_MINUTES', 60)
        self.alert_threshold = getattr(settings, 'CREDENTIAL_ALERT_THRESHOLD', 1)
        
        # Monitoring state
        self.is_running = False
        self.monitor_thread = None
        self.alerts = []
        self.last_check_time = None
        self.check_count = 0
        self.issue_count = 0
        self.auto_fix_count = 0
        
        # Alert callbacks
        self.alert_callbacks = []
        
        self._initialize_monitoring()
    
    def _initialize_monitoring(self):
        """Initialize the monitoring system."""
        console_log = {
            'service': 'CredentialMonitor',
            'action': 'initialized',
            'monitoring_enabled': self.monitoring_enabled,
            'auto_fix_enabled': self.auto_fix_enabled,
            'check_interval_minutes': self.check_interval,
            'timestamp': timezone.now().isoformat()
        }
        logger.info(f"[CREDENTIAL_MONITOR_INIT] {json.dumps(console_log)}")
        print(f"[CREDENTIAL_MONITOR_INIT] {json.dumps(console_log)}")
    
    def start_monitoring(self):
        """Start the automated monitoring system."""
        if not self.monitoring_enabled:
            print("⚠️  Credential monitoring is disabled in settings")
            return False
        
        if self.is_running:
            print("⚠️  Monitoring is already running")
            return False
        
        print(f"🚀 Starting credential monitoring (interval: {self.check_interval} minutes)")
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        console_log = {
            'service': 'CredentialMonitor',
            'action': 'monitoring_started',
            'thread_id': self.monitor_thread.ident,
            'timestamp': timezone.now().isoformat()
        }
        logger.info(f"[CREDENTIAL_MONITOR_START] {json.dumps(console_log)}")
        print(f"[CREDENTIAL_MONITOR_START] {json.dumps(console_log)}")
        
        return True
    
    def stop_monitoring(self):
        """Stop the automated monitoring system."""
        if not self.is_running:
            print("⚠️  Monitoring is not running")
            return False
        
        print("🛑 Stopping credential monitoring...")
        self.is_running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        console_log = {
            'service': 'CredentialMonitor',
            'action': 'monitoring_stopped',
            'total_checks': self.check_count,
            'total_issues': self.issue_count,
            'total_auto_fixes': self.auto_fix_count,
            'timestamp': timezone.now().isoformat()
        }
        logger.info(f"[CREDENTIAL_MONITOR_STOP] {json.dumps(console_log)}")
        print(f"[CREDENTIAL_MONITOR_STOP] {json.dumps(console_log)}")
        
        return True
    
    def _monitoring_loop(self):
        """Main monitoring loop that runs in a separate thread."""
        print(f"🔄 Credential monitoring loop started")
        
        while self.is_running:
            try:
                self._perform_check()
                
                # Wait for next check interval
                for _ in range(self.check_interval * 60):  # Convert minutes to seconds
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                console_log = {
                    'service': 'CredentialMonitor',
                    'action': 'monitoring_error',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                }
                logger.error(f"[CREDENTIAL_MONITOR_ERROR] {json.dumps(console_log)}")
                print(f"[CREDENTIAL_MONITOR_ERROR] {json.dumps(console_log)}")
                
                # Sleep for a short time before retrying
                time.sleep(60)
        
        print(f"🔄 Credential monitoring loop stopped")
    
    def _perform_check(self):
        """Perform a comprehensive credential check."""
        self.check_count += 1
        self.last_check_time = timezone.now()
        
        console_log = {
            'service': 'CredentialMonitor',
            'action': 'check_started',
            'check_number': self.check_count,
            'timestamp': self.last_check_time.isoformat()
        }
        logger.info(f"[CREDENTIAL_CHECK_START] {json.dumps(console_log)}")
        print(f"[CREDENTIAL_CHECK_START] Check #{self.check_count} at {self.last_check_time.isoformat()}")
        
        # Validate all credentials
        validation_results = self.service.validate_all_credentials()
        
        # Check for issues
        issues_found = validation_results['invalid_accounts']
        
        if issues_found > 0:
            self.issue_count += issues_found
            self._handle_credential_issues(validation_results)
        
        # Generate monitoring report
        self._generate_check_report(validation_results)
        
        console_log = {
            'service': 'CredentialMonitor',
            'action': 'check_completed',
            'check_number': self.check_count,
            'issues_found': issues_found,
            'timestamp': timezone.now().isoformat()
        }
        logger.info(f"[CREDENTIAL_CHECK_COMPLETE] {json.dumps(console_log)}")
        print(f"[CREDENTIAL_CHECK_COMPLETE] Check #{self.check_count} - Issues: {issues_found}")
    
    def _handle_credential_issues(self, validation_results: Dict[str, Any]):
        """Handle detected credential issues."""
        for account_key, status in validation_results['protected_accounts_status'].items():
            if not status['is_valid']:
                # Create alert
                alert = self._create_alert(account_key, status)
                self.alerts.append(alert)
                
                # Trigger callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert, status)
                    except Exception as e:
                        logger.error(f"Alert callback failed: {e}")
                
                # Attempt auto-fix if enabled
                if self.auto_fix_enabled:
                    self._attempt_auto_fix(alert, account_key)
    
    def _create_alert(self, account_key: str, status: Dict[str, Any]) -> MonitoringAlert:
        """Create a monitoring alert for credential issues."""
        # Determine severity based on issues
        severity = 'MEDIUM'
        if not status['authentication_works']:
            severity = 'HIGH'
        if account_key == 'admin' and not status['authentication_works']:
            severity = 'CRITICAL'
        
        # Create issue description
        issues = status.get('issues', [])
        description = f"Credential issues detected: {', '.join(issues)}"
        
        alert = MonitoringAlert(
            alert_id=f"CRED_{account_key}_{int(time.time())}",
            severity=severity,
            account=account_key,
            issue_type='CREDENTIAL_CORRUPTION',
            description=description,
            timestamp=timezone.now()
        )
        
        console_log = {
            'service': 'CredentialMonitor',
            'action': 'alert_created',
            'alert_id': alert.alert_id,
            'severity': alert.severity,
            'account': alert.account,
            'issues_count': len(issues),
            'timestamp': alert.timestamp.isoformat()
        }
        logger.warning(f"[CREDENTIAL_ALERT] {json.dumps(console_log)}")
        print(f"[CREDENTIAL_ALERT] {alert.severity} - {alert.account}: {alert.description}")
        
        return alert
    
    def _attempt_auto_fix(self, alert: MonitoringAlert, account_key: str):
        """Attempt to automatically fix credential issues."""
        if not self.auto_fix_enabled:
            return
        
        try:
            console_log = {
                'service': 'CredentialMonitor',
                'action': 'auto_fix_attempt',
                'alert_id': alert.alert_id,
                'account': account_key,
                'timestamp': timezone.now().isoformat()
            }
            logger.info(f"[CREDENTIAL_AUTO_FIX_ATTEMPT] {json.dumps(console_log)}")
            print(f"[CREDENTIAL_AUTO_FIX_ATTEMPT] Attempting to fix {account_key}")
            
            # Attempt the fix
            fix_result = self.service.fix_account_credentials(account_key, force=True)
            
            if fix_result['success']:
                # Mark alert as resolved
                alert.resolved = True
                alert.resolution_action = f"Auto-fixed: {', '.join(fix_result['actions_taken'])}"
                alert.resolution_timestamp = timezone.now()
                self.auto_fix_count += 1
                
                console_log = {
                    'service': 'CredentialMonitor',
                    'action': 'auto_fix_success',
                    'alert_id': alert.alert_id,
                    'account': account_key,
                    'actions_taken': len(fix_result['actions_taken']),
                    'timestamp': timezone.now().isoformat()
                }
                logger.info(f"[CREDENTIAL_AUTO_FIX_SUCCESS] {json.dumps(console_log)}")
                print(f"[CREDENTIAL_AUTO_FIX_SUCCESS] ✅ Fixed {account_key}")
                
            else:
                console_log = {
                    'service': 'CredentialMonitor',
                    'action': 'auto_fix_failed',
                    'alert_id': alert.alert_id,
                    'account': account_key,
                    'error': fix_result.get('error', 'Unknown error'),
                    'timestamp': timezone.now().isoformat()
                }
                logger.error(f"[CREDENTIAL_AUTO_FIX_FAILED] {json.dumps(console_log)}")
                print(f"[CREDENTIAL_AUTO_FIX_FAILED] ❌ Failed to fix {account_key}: {fix_result.get('error')}")
                
        except Exception as e:
            console_log = {
                'service': 'CredentialMonitor',
                'action': 'auto_fix_exception',
                'alert_id': alert.alert_id,
                'account': account_key,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
            logger.error(f"[CREDENTIAL_AUTO_FIX_EXCEPTION] {json.dumps(console_log)}")
            print(f"[CREDENTIAL_AUTO_FIX_EXCEPTION] ❌ Exception fixing {account_key}: {e}")
    
    def _generate_check_report(self, validation_results: Dict[str, Any]):
        """Generate a report for the current check."""
        report = {
            'monitoring_service': 'CredentialMonitor',
            'check_number': self.check_count,
            'timestamp': timezone.now().isoformat(),
            'validation_results': validation_results,
            'monitoring_stats': {
                'total_checks': self.check_count,
                'total_issues': self.issue_count,
                'total_auto_fixes': self.auto_fix_count,
                'active_alerts': len([a for a in self.alerts if not a.resolved]),
                'resolved_alerts': len([a for a in self.alerts if a.resolved])
            }
        }
        
        # Log the report
        logger.info(f"[CREDENTIAL_MONITOR_REPORT] {json.dumps(report)}")
    
    def add_alert_callback(self, callback: Callable):
        """Add a callback function to be called when alerts are created."""
        self.alert_callbacks.append(callback)
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get the current monitoring status."""
        return {
            'monitoring_enabled': self.monitoring_enabled,
            'auto_fix_enabled': self.auto_fix_enabled,
            'is_running': self.is_running,
            'check_interval_minutes': self.check_interval,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'statistics': {
                'total_checks': self.check_count,
                'total_issues': self.issue_count,
                'total_auto_fixes': self.auto_fix_count,
                'active_alerts': len([a for a in self.alerts if not a.resolved]),
                'resolved_alerts': len([a for a in self.alerts if a.resolved])
            },
            'recent_alerts': [
                {
                    'alert_id': alert.alert_id,
                    'severity': alert.severity,
                    'account': alert.account,
                    'description': alert.description,
                    'timestamp': alert.timestamp.isoformat(),
                    'resolved': alert.resolved
                }
                for alert in self.alerts[-10:]  # Last 10 alerts
            ]
        }
    
    def get_health_dashboard(self) -> Dict[str, Any]:
        """Get a comprehensive health dashboard."""
        # Get system health report
        health_report = self.service.get_system_health_report()
        
        # Get protection report
        protection_report = get_protection_report()
        
        # Combine all information
        dashboard = {
            'timestamp': timezone.now().isoformat(),
            'system_status': 'HEALTHY' if self.issue_count == 0 else 'DEGRADED',
            'monitoring_status': self.get_monitoring_status(),
            'credential_health': health_report,
            'protection_status': protection_report,
            'recommendations': []
        }
        
        # Generate recommendations
        if not self.is_running:
            dashboard['recommendations'].append("Start automated monitoring")
        
        if self.issue_count > 0:
            dashboard['recommendations'].append("Investigate and resolve credential issues")
        
        if len(self.alerts) > 10:
            dashboard['recommendations'].append("Review and clear old alerts")
        
        return dashboard


# Global monitor instance
credential_monitor = CredentialMonitor()


def start_monitoring():
    """Start the credential monitoring system."""
    return credential_monitor.start_monitoring()


def stop_monitoring():
    """Stop the credential monitoring system."""
    return credential_monitor.stop_monitoring()


def get_monitoring_status():
    """Get the current monitoring status."""
    return credential_monitor.get_monitoring_status()


def get_health_dashboard():
    """Get the comprehensive health dashboard."""
    return credential_monitor.get_health_dashboard()


# Example alert callback
def console_alert_callback(alert: MonitoringAlert, status: Dict[str, Any]):
    """Example callback that prints alerts to console."""
    print(f"🚨 ALERT: {alert.severity} - {alert.account} - {alert.description}")


# Register default callbacks
credential_monitor.add_alert_callback(console_alert_callback)


if __name__ == '__main__':
    """Command-line interface for the monitoring system."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            print("Starting credential monitoring system...")
            if start_monitoring():
                print("✅ Monitoring started successfully")
                try:
                    # Keep the script running
                    while credential_monitor.is_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping monitoring...")
                    stop_monitoring()
            else:
                print("❌ Failed to start monitoring")
                
        elif command == 'status':
            status = get_monitoring_status()
            print(json.dumps(status, indent=2))
            
        elif command == 'dashboard':
            dashboard = get_health_dashboard()
            print(json.dumps(dashboard, indent=2))
            
        elif command == 'stop':
            if stop_monitoring():
                print("✅ Monitoring stopped successfully")
            else:
                print("❌ Monitoring was not running")
        else:
            print("Usage: python automated_credential_monitor.py [start|stop|status|dashboard]")
    else:
        print("Usage: python automated_credential_monitor.py [start|stop|status|dashboard]")