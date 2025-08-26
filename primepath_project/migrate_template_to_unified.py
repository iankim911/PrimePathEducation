#!/usr/bin/env python
"""
Phase 3, Day 1 Afternoon: Template Migration Helper
Helps migrate templates from base.html/routinetest_base.html to unified_base.html
"""

import os
import sys
import re
from pathlib import Path
import shutil
from datetime import datetime

class TemplateMigrator:
    """Migrate templates to use unified_base.html."""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent
        self.templates_dir = self.project_root / 'templates'
        self.backup_dir = self.project_root / f'migration_backups_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        self.migration_log = []
        
    def migrate_template(self, template_path, force=False):
        """
        Migrate a single template to use unified_base.html.
        
        Args:
            template_path: Path to the template file
            force: Force migration even if template seems complex
        """
        template_path = Path(template_path)
        
        if not template_path.exists():
            print(f"❌ Template not found: {template_path}")
            return False
            
        # Read template content
        with open(template_path, 'r') as f:
            content = f.read()
            original_content = content
            
        # Check which base template it extends
        extends_pattern = r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}'
        match = re.search(extends_pattern, content)
        
        if not match:
            print(f"⚠️  {template_path.name} does not extend any base template")
            return False
            
        base_template = match.group(1)
        
        if base_template == 'unified_base.html':
            print(f"✅ {template_path.name} already uses unified_base.html")
            return True
            
        if base_template not in ['base.html', 'routinetest_base.html']:
            print(f"⚠️  {template_path.name} extends {base_template} (not a target for migration)")
            return False
            
        print(f"\n📄 Migrating: {template_path.name}")
        print(f"   Current base: {base_template}")
        
        # Backup original
        if not self.dry_run:
            self._backup_template(template_path)
            
        # Replace extends statement
        content = re.sub(
            extends_pattern,
            '{% extends "unified_base.html" %}',
            content
        )
        
        # Add migration comment
        migration_comment = f"""{{%% comment %%}}
Migrated to unified_base.html on {datetime.now().strftime('%Y-%m-%d')}
Original base template: {base_template}
{{%% endcomment %%}}
"""
        content = content.replace('{% extends "unified_base.html" %}', 
                                 f'{{% extends "unified_base.html" %}}\n{migration_comment}')
        
        # Handle module-specific blocks based on original base
        if base_template == 'routinetest_base.html':
            # Add module name block for routinetest templates
            if '{% block module_name %}' not in content:
                content = self._add_after_extends(content, '{% block module_name %}primepath_routinetest{% endblock %}')
                
            # Check for font size customization
            if '{% block base_font_size %}' not in content and '17px' in original_content:
                content = self._add_after_extends(content, '{% block base_font_size %}17px{% endblock %}')
                
        elif base_template == 'base.html':
            # Add module name block for placement templates
            if '{% block module_name %}' not in content:
                # Detect module from path
                if 'placement' in str(template_path).lower():
                    content = self._add_after_extends(content, '{% block module_name %}placement_test{% endblock %}')
                    
        # Log changes
        changes = []
        if content != original_content:
            changes.append(f"✓ Changed extends from {base_template} to unified_base.html")
            if '{% block module_name %}' in content and '{% block module_name %}' not in original_content:
                changes.append("✓ Added module_name block")
            if '{% block base_font_size %}' in content and '{% block base_font_size %}' not in original_content:
                changes.append("✓ Added base_font_size block")
                
        # Write changes
        if not self.dry_run and content != original_content:
            with open(template_path, 'w') as f:
                f.write(content)
            print(f"✅ Migrated successfully!")
        else:
            print(f"🔍 DRY RUN - Would make these changes:")
            
        for change in changes:
            print(f"   {change}")
            
        self.migration_log.append({
            'template': template_path.name,
            'original_base': base_template,
            'changes': changes,
            'status': 'migrated' if not self.dry_run else 'would_migrate'
        })
        
        return True
        
    def _add_after_extends(self, content, block_to_add):
        """Add a block after the extends statement."""
        extends_pattern = r'({%\s*extends\s+["\'][^"\']+["\']\s*%})'
        replacement = f'\\1\n{block_to_add}'
        return re.sub(extends_pattern, replacement, content)
        
    def _backup_template(self, template_path):
        """Create a backup of the template."""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            
        relative_path = template_path.relative_to(self.templates_dir)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(template_path, backup_path)
        print(f"   📦 Backed up to: {backup_path}")
        
    def batch_migrate(self, templates, force=False):
        """Migrate multiple templates."""
        print(f"\n{'=' * 80}")
        print(f"TEMPLATE MIGRATION {'(DRY RUN)' if self.dry_run else ''}")
        print(f"{'=' * 80}")
        
        successful = 0
        failed = 0
        
        for template in templates:
            template_path = self.templates_dir / template
            if self.migrate_template(template_path, force):
                successful += 1
            else:
                failed += 1
                
        print(f"\n{'=' * 80}")
        print(f"MIGRATION SUMMARY")
        print(f"{'=' * 80}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        
        if self.dry_run:
            print(f"\n⚠️  This was a DRY RUN. No files were changed.")
            print(f"To apply changes, run with --apply flag")
            
        return self.migration_log
        
    def find_candidates(self):
        """Find all templates that extend base.html or routinetest_base.html."""
        candidates = {
            'base.html': [],
            'routinetest_base.html': []
        }
        
        for html_file in self.templates_dir.rglob('*.html'):
            if html_file.name in ['base.html', 'routinetest_base.html', 'unified_base.html']:
                continue
                
            with open(html_file, 'r') as f:
                content = f.read()
                
            if 'extends "base.html"' in content or "extends 'base.html'" in content:
                candidates['base.html'].append(html_file.relative_to(self.templates_dir))
            elif 'extends "routinetest_base.html"' in content or "extends 'routinetest_base.html'" in content:
                candidates['routinetest_base.html'].append(html_file.relative_to(self.templates_dir))
                
        return candidates


def main():
    """Main migration script."""
    
    # Parse arguments
    dry_run = '--apply' not in sys.argv
    show_candidates = '--list' in sys.argv
    
    migrator = TemplateMigrator(dry_run=dry_run)
    
    if show_candidates:
        # Show migration candidates
        candidates = migrator.find_candidates()
        
        print("\n" + "=" * 80)
        print("MIGRATION CANDIDATES")
        print("=" * 80)
        
        print(f"\nTemplates extending base.html ({len(candidates['base.html'])}):")
        for template in candidates['base.html'][:10]:
            print(f"  - {template}")
        if len(candidates['base.html']) > 10:
            print(f"  ... and {len(candidates['base.html']) - 10} more")
            
        print(f"\nTemplates extending routinetest_base.html ({len(candidates['routinetest_base.html'])}):")
        for template in candidates['routinetest_base.html'][:10]:
            print(f"  - {template}")
        if len(candidates['routinetest_base.html']) > 10:
            print(f"  ... and {len(candidates['routinetest_base.html']) - 10} more")
            
        print(f"\nTotal candidates: {len(candidates['base.html']) + len(candidates['routinetest_base.html'])}")
        print("\nTo migrate all: python migrate_template_to_unified.py --migrate-all [--apply]")
        print("To migrate specific: python migrate_template_to_unified.py template1.html template2.html [--apply]")
        
    elif '--migrate-all' in sys.argv:
        # Migrate all candidates
        candidates = migrator.find_candidates()
        all_templates = candidates['base.html'] + candidates['routinetest_base.html']
        
        if input(f"\nMigrate {len(all_templates)} templates? (y/N): ").lower() == 'y':
            migrator.batch_migrate(all_templates)
    else:
        # Migrate specific templates
        templates = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
        
        if templates:
            migrator.batch_migrate(templates)
        else:
            print("Usage:")
            print("  List candidates:    python migrate_template_to_unified.py --list")
            print("  Migrate all:        python migrate_template_to_unified.py --migrate-all [--apply]")
            print("  Migrate specific:   python migrate_template_to_unified.py template1.html template2.html [--apply]")
            print("\nAdd --apply to actually modify files (otherwise runs in dry-run mode)")


if __name__ == '__main__':
    main()