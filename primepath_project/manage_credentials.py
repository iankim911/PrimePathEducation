"""
Django Management Command: Credential Management
==============================================

Provides comprehensive user credential management functionality for production deployments.

Usage:
    python manage.py manage_credentials --validate
    python manage.py manage_credentials --fix teacher1
    python manage.py manage_credentials --health-report
    python manage.py manage_credentials --protect-accounts

Author: Claude Code AI System
Date: August 25, 2025
"""
import os
import sys
import django
import json
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from user_credential_service import credential_service


class Command:
    """Command-line interface for user credential management."""
    
    help = 'Manage user credentials and ensure authentication system integrity'
    
    def __init__(self):
        self.service = credential_service
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate all protected user credentials'
        )
        
        parser.add_argument(
            '--fix',
            type=str,
            help='Fix credentials for specific account (e.g., teacher1, admin)'
        )
        
        parser.add_argument(
            '--health-report',
            action='store_true',
            help='Generate comprehensive authentication system health report'
        )
        
        parser.add_argument(
            '--protect-accounts',
            action='store_true',
            help='Add protection markers to critical accounts'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force operations even in production (use with caution)'
        )
        
        parser.add_argument(
            '--output-file',
            type=str,
            help='Save results to specified file'
        )
    
    def handle(self, **options):
        """Handle the management command."""
        print("="*80)
        print("USER CREDENTIAL MANAGEMENT SYSTEM")
        print("="*80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Service Version: 1.0")
        print("")
        
        results = {}
        
        if options.get('validate'):
            print("🔍 VALIDATING ALL PROTECTED CREDENTIALS...")
            print("-" * 50)
            results = self._handle_validate(options)
            
        elif options.get('fix'):
            account = options['fix']
            print(f"🔧 FIXING CREDENTIALS FOR: {account}")
            print("-" * 50)
            results = self._handle_fix(account, options)
            
        elif options.get('health_report'):
            print("📊 GENERATING SYSTEM HEALTH REPORT...")
            print("-" * 50)
            results = self._handle_health_report(options)
            
        elif options.get('protect_accounts'):
            print("🛡️  PROTECTING CRITICAL ACCOUNTS...")
            print("-" * 50)
            results = self._handle_protect_accounts(options)
            
        else:
            self._show_usage()
            return
        
        # Save results to file if requested
        if options.get('output_file') and results:
            self._save_results(results, options['output_file'])
        
        print("\n" + "="*80)
        print("✅ CREDENTIAL MANAGEMENT OPERATION COMPLETE")
        print("="*80)
    
    def _handle_validate(self, options) -> dict:
        """Handle credential validation."""
        results = self.service.validate_all_credentials()
        
        # Display summary
        print(f"Total Accounts Checked: {results['total_accounts_checked']}")
        print(f"Valid Accounts: {results['valid_accounts']}")
        print(f"Invalid Accounts: {results['invalid_accounts']}")
        print(f"Overall Status: {results['overall_status']}")
        
        if results['invalid_accounts'] > 0:
            print(f"\n⚠️  ISSUES FOUND:")
            for account, status in results['protected_accounts_status'].items():
                if not status['is_valid']:
                    print(f"\n❌ {account}:")
                    for issue in status['issues']:
                        print(f"   • {issue}")
        else:
            print(f"\n✅ All protected accounts are healthy!")
        
        # Show recommendations
        if results['recommendations']:
            print(f"\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        return results
    
    def _handle_fix(self, account: str, options) -> dict:
        """Handle credential fixing for specific account."""
        try:
            force = options.get('force', False)
            results = self.service.fix_account_credentials(account, force=force)
            
            print(f"Account: {results['account_key']}")
            print(f"Username: {results['username']}")
            print(f"Success: {results['success']}")
            
            if results['success']:
                print(f"\n✅ CREDENTIALS FIXED SUCCESSFULLY")
                print(f"Actions taken:")
                for i, action in enumerate(results['actions_taken'], 1):
                    print(f"   {i}. {action}")
            else:
                print(f"\n❌ CREDENTIAL FIX FAILED")
                if 'error' in results:
                    print(f"Error: {results['error']}")
            
            return results
            
        except ValueError as e:
            print(f"❌ Invalid account: {e}")
            return {'error': str(e)}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {'error': str(e)}
    
    def _handle_health_report(self, options) -> dict:
        """Handle health report generation."""
        results = self.service.get_system_health_report()
        
        print(f"Environment: {results['environment']}")
        print(f"Debug Mode: {results['debug_mode']}")
        print(f"Service Version: {results['service_version']}")
        
        # User Statistics
        stats = results['user_statistics']
        print(f"\n👥 USER STATISTICS:")
        print(f"   Total Users: {stats['total_users']}")
        print(f"   Active Users: {stats['active_users']}")
        print(f"   Staff Users: {stats['staff_users']}")
        print(f"   Superusers: {stats['superusers']}")
        print(f"   Teachers with Profiles: {stats['teachers_with_profiles']}")
        print(f"   Students with Profiles: {stats['students_with_profiles']}")
        print(f"   Users without Profiles: {stats['users_without_profiles']}")
        
        # Authentication Health
        health = results['authentication_health']
        print(f"\n🏥 AUTHENTICATION HEALTH:")
        print(f"   Protected Accounts Healthy: {health['protected_accounts_healthy']}/{health['protected_accounts_total']}")
        print(f"   Health Percentage: {health['health_percentage']:.1f}%")
        print(f"   Authentication Services: {'✅ Active' if health['authentication_services_active'] else '❌ Issues'}")
        print(f"   Profile Sync: {'✅ Healthy' if health['profile_sync_healthy'] else '❌ Issues'}")
        
        # Recommendations
        if results['recommendations']:
            print(f"\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n⏰ Next Check Recommended: {results['next_check_recommended']}")
        
        return results
    
    def _handle_protect_accounts(self, options) -> dict:
        """Handle account protection setup."""
        protected_count = 0
        results = {'protected_accounts': []}
        
        for account_key in self.service.PROTECTED_ACCOUNTS.keys():
            if self.service.protect_account_from_tests(account_key):
                protected_count += 1
                results['protected_accounts'].append(account_key)
                print(f"✅ Protected: {account_key}")
            else:
                print(f"❌ Failed to protect: {account_key}")
        
        print(f"\n🛡️  Protected {protected_count} accounts from test corruption")
        results['protected_count'] = protected_count
        
        return results
    
    def _save_results(self, results: dict, filename: str):
        """Save results to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    def _show_usage(self):
        """Show usage information."""
        print("🚀 CREDENTIAL MANAGEMENT SYSTEM")
        print("\nAvailable operations:")
        print("  --validate              Validate all protected credentials")
        print("  --fix ACCOUNT          Fix credentials for specific account")
        print("  --health-report        Generate comprehensive health report")
        print("  --protect-accounts     Add protection to critical accounts")
        print("\nOptions:")
        print("  --force                Force operations in production")
        print("  --output-file FILE     Save results to JSON file")
        print("\nExamples:")
        print("  python manage_credentials.py --validate")
        print("  python manage_credentials.py --fix teacher1")
        print("  python manage_credentials.py --health-report --output-file health.json")
        print("  python manage_credentials.py --protect-accounts")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage user credentials and authentication system')
    command = Command()
    command.add_arguments(parser)
    
    args = parser.parse_args()
    command.handle(**vars(args))


if __name__ == '__main__':
    main()