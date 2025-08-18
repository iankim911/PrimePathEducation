#!/usr/bin/env python
"""
Migrate from 12 classes to 60 classes with proper classification
Updates existing assignments and creates new class structure

Created: August 18, 2025
"""
import os
import sys
import django
import random
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import (
    TeacherClassAssignment,
    ClassAccessRequest,
    AccessAuditLog
)

# Old to new class mapping
OLD_TO_NEW_MAPPING = {
    'CLASS_7A': ['MIDDLE_7A', 'MIDDLE_7B'],  # Science/Math focus
    'CLASS_7B': ['MIDDLE_7C', 'MIDDLE_7D'],  # Language/Tech focus
    'CLASS_7C': ['MIDDLE_7E', 'MIDDLE_7F'],  # Arts/General
    'CLASS_8A': ['MIDDLE_8A', 'MIDDLE_8B'],  # Science/Math focus
    'CLASS_8B': ['MIDDLE_8C', 'MIDDLE_8D'],  # Language/Tech focus
    'CLASS_8C': ['MIDDLE_8E', 'MIDDLE_8F'],  # Arts/General
    'CLASS_9A': ['MIDDLE_9A', 'MIDDLE_9B'],  # Science/Math focus
    'CLASS_9B': ['MIDDLE_9C', 'MIDDLE_9D'],  # Language/Tech focus
    'CLASS_9C': ['MIDDLE_9E', 'MIDDLE_9F'],  # Arts/General
    'CLASS_10A': ['HIGH_10A', 'HIGH_10B'],   # STEM/Business
    'CLASS_10B': ['HIGH_10C', 'HIGH_10D'],   # Liberal Arts/Creative
    'CLASS_10C': ['HIGH_10E', 'HIGH_10F'],   # Tech/IB
}

# New classes for random assignment
NEW_CLASSES = [
    # Primary classes (will be randomly assigned)
    'PRIMARY_1A', 'PRIMARY_1B', 'PRIMARY_1C', 'PRIMARY_1D',
    'PRIMARY_2A', 'PRIMARY_2B', 'PRIMARY_2C', 'PRIMARY_2D',
    'PRIMARY_3A', 'PRIMARY_3B', 'PRIMARY_3C', 'PRIMARY_3D',
    'PRIMARY_4A', 'PRIMARY_4B', 'PRIMARY_4C', 'PRIMARY_4D',
    'PRIMARY_5A', 'PRIMARY_5B', 'PRIMARY_5C', 'PRIMARY_5D',
    'PRIMARY_6A', 'PRIMARY_6B', 'PRIMARY_6C', 'PRIMARY_6D',
    
    # Additional High school classes
    'HIGH_11A', 'HIGH_11B', 'HIGH_11C', 'HIGH_11D', 'HIGH_11E', 'HIGH_11F',
    'HIGH_12A', 'HIGH_12B', 'HIGH_12C', 'HIGH_12D', 'HIGH_12E', 'HIGH_12F',
]

def migrate_existing_assignments():
    """Migrate existing 12-class assignments to new 60-class structure"""
    
    print("\n" + "="*80)
    print("MIGRATING EXISTING CLASS ASSIGNMENTS")
    print("="*80)
    
    admin_user = User.objects.filter(is_superuser=True).first()
    migrated_count = 0
    
    # Get all active assignments with old class codes
    old_assignments = TeacherClassAssignment.objects.filter(
        is_active=True,
        class_code__in=OLD_TO_NEW_MAPPING.keys()
    )
    
    print(f"Found {old_assignments.count()} assignments to migrate")
    
    for assignment in old_assignments:
        old_class = assignment.class_code
        new_classes = OLD_TO_NEW_MAPPING.get(old_class, [])
        
        if new_classes:
            print(f"\n🔄 Migrating {assignment.teacher.name} from {old_class}")
            
            # Deactivate old assignment
            assignment.is_active = False
            assignment.notes = f"Migrated to new 60-class structure on {datetime.now()}"
            assignment.save()
            
            # Create new assignments
            for new_class in new_classes:
                # Check if assignment already exists
                existing = TeacherClassAssignment.objects.filter(
                    teacher=assignment.teacher,
                    class_code=new_class,
                    is_active=True
                ).first()
                
                if not existing:
                    new_assignment = TeacherClassAssignment.objects.create(
                        teacher=assignment.teacher,
                        class_code=new_class,
                        access_level=assignment.access_level,
                        assigned_by=admin_user,
                        notes=f"Migrated from {old_class} - {assignment.notes}",
                        is_active=True
                    )
                    
                    print(f"   ✅ Created: {new_class}")
                    migrated_count += 1
                    
                    # Create audit log
                    AccessAuditLog.log_action(
                        action='ASSIGNMENT_CREATED',
                        teacher=assignment.teacher,
                        class_code=new_class,
                        user=admin_user,
                        details={
                            'migration': True,
                            'old_class': old_class,
                            'access_level': assignment.access_level
                        },
                        assignment=new_assignment
                    )
                else:
                    print(f"   ⚠️ Exists: {new_class}")
    
    print(f"\n✅ Migration completed: {migrated_count} new assignments created")
    return migrated_count

def assign_teachers_to_new_classes():
    """Assign teachers to newly added classes (Primary and High School 11-12)"""
    
    print("\n" + "="*80)
    print("ASSIGNING TEACHERS TO NEW CLASSES")
    print("="*80)
    
    admin_user = User.objects.filter(is_superuser=True).first()
    assignment_count = 0
    
    # Get all teachers
    teachers = list(Teacher.objects.all())
    print(f"Working with {len(teachers)} teachers")
    
    # Assign primary classes (each teacher gets 1-2 primary classes)
    primary_classes = [c for c in NEW_CLASSES if 'PRIMARY' in c]
    print(f"\nAssigning {len(primary_classes)} primary classes...")
    
    for teacher in teachers:
        # 70% chance to get primary classes
        if random.random() < 0.7:
            num_primary = random.randint(1, 2)
            assigned_primary = random.sample(primary_classes, min(num_primary, len(primary_classes)))
            
            for class_code in assigned_primary:
                # Check if assignment exists
                existing = TeacherClassAssignment.objects.filter(
                    teacher=teacher,
                    class_code=class_code,
                    is_active=True
                ).first()
                
                if not existing:
                    # Mostly full access for primary
                    access_level = random.choice(['FULL', 'FULL', 'FULL', 'VIEW'])
                    
                    assignment = TeacherClassAssignment.objects.create(
                        teacher=teacher,
                        class_code=class_code,
                        access_level=access_level,
                        assigned_by=admin_user,
                        notes=f"60-class structure assignment",
                        is_active=True
                    )
                    
                    assignment_count += 1
                    print(f"   {teacher.name} → {class_code} ({access_level})")
    
    # Assign high school 11-12 classes
    high_classes = [c for c in NEW_CLASSES if 'HIGH_1' in c]
    print(f"\nAssigning {len(high_classes)} high school classes...")
    
    for teacher in teachers:
        # 50% chance to get high school classes
        if random.random() < 0.5:
            num_high = random.randint(1, 3)
            assigned_high = random.sample(high_classes, min(num_high, len(high_classes)))
            
            for class_code in assigned_high:
                # Check if assignment exists
                existing = TeacherClassAssignment.objects.filter(
                    teacher=teacher,
                    class_code=class_code,
                    is_active=True
                ).first()
                
                if not existing:
                    access_level = random.choice(['FULL', 'FULL', 'VIEW', 'CO_TEACHER'])
                    
                    assignment = TeacherClassAssignment.objects.create(
                        teacher=teacher,
                        class_code=class_code,
                        access_level=access_level,
                        assigned_by=admin_user,
                        notes=f"60-class structure assignment",
                        is_active=True
                    )
                    
                    assignment_count += 1
                    print(f"   {teacher.name} → {class_code} ({access_level})")
    
    print(f"\n✅ New assignments completed: {assignment_count} assignments created")
    return assignment_count

def create_sample_requests():
    """Create sample access requests for new classes"""
    
    print("\n" + "="*80)
    print("CREATING SAMPLE ACCESS REQUESTS")
    print("="*80)
    
    # Get random teachers
    teachers = list(Teacher.objects.all())
    request_count = 0
    
    # Create 8-10 random requests
    for i in range(random.randint(8, 10)):
        teacher = random.choice(teachers)
        
        # Find classes they don't have access to
        current_classes = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).values_list('class_code', flat=True)
        
        all_classes = [choice[0] for choice in 
                      TeacherClassAssignment._meta.get_field('class_code').choices]
        available_classes = [c for c in all_classes if c not in current_classes]
        
        if available_classes:
            requested_class = random.choice(available_classes)
            
            # Check if request already exists
            existing_request = ClassAccessRequest.objects.filter(
                teacher=teacher,
                class_code=requested_class,
                status='PENDING'
            ).first()
            
            if not existing_request:
                request_type = random.choice(['PERMANENT', 'PERMANENT', 'TEMPORARY'])
                reasons = [
                    'CURRICULUM_EXPERTISE',
                    'SCHEDULE_OPTIMIZATION', 
                    'CO_TEACHING',
                    'NEW_ASSIGNMENT'
                ]
                reason = random.choice(reasons)
                
                # Create request
                access_request = ClassAccessRequest.objects.create(
                    teacher=teacher,
                    class_code=requested_class,
                    request_type=request_type,
                    reason_code=reason,
                    reason_text=f"Request for {requested_class}: {reason.replace('_', ' ').lower()} in new 60-class structure",
                    requested_access_level=random.choice(['FULL', 'FULL', 'VIEW']),
                    status='PENDING'
                )
                
                request_count += 1
                print(f"   {teacher.name} requesting {requested_class} ({request_type})")
    
    print(f"\n✅ Sample requests created: {request_count}")
    return request_count

def generate_statistics():
    """Generate statistics for the new structure"""
    
    print("\n" + "="*80)
    print("60-CLASS STRUCTURE STATISTICS")
    print("="*80)
    
    # Count assignments by category
    from primepath_routinetest.models.class_constants import CLASS_CATEGORIES
    
    stats = {}
    for category, classes in CLASS_CATEGORIES.items():
        assignments = TeacherClassAssignment.objects.filter(
            class_code__in=classes,
            is_active=True
        ).count()
        stats[category] = {
            'classes': len(classes),
            'assignments': assignments,
            'avg_per_class': assignments / len(classes) if classes else 0
        }
    
    print("\nASSIGNMENT DISTRIBUTION:")
    total_assignments = 0
    for category, data in stats.items():
        print(f"  {category}: {data['assignments']} assignments across {data['classes']} classes")
        print(f"    Average: {data['avg_per_class']:.1f} teachers per class")
        total_assignments += data['assignments']
    
    print(f"\nTOTAL ACTIVE ASSIGNMENTS: {total_assignments}")
    
    # Teachers with assignments
    teachers_with_assignments = TeacherClassAssignment.objects.filter(
        is_active=True
    ).values('teacher').distinct().count()
    
    total_teachers = Teacher.objects.count()
    
    print(f"TEACHERS WITH ASSIGNMENTS: {teachers_with_assignments}/{total_teachers}")
    
    # Pending requests
    pending_requests = ClassAccessRequest.objects.filter(status='PENDING').count()
    print(f"PENDING REQUESTS: {pending_requests}")
    
    # Classes without teachers
    all_class_codes = [choice[0] for choice in 
                      TeacherClassAssignment._meta.get_field('class_code').choices]
    
    assigned_classes = set(TeacherClassAssignment.objects.filter(
        is_active=True
    ).values_list('class_code', flat=True))
    
    unassigned_classes = [c for c in all_class_codes if c not in assigned_classes]
    
    print(f"CLASSES WITHOUT TEACHERS: {len(unassigned_classes)}")
    if unassigned_classes:
        print("  Unassigned classes:", unassigned_classes[:10], "..." if len(unassigned_classes) > 10 else "")

def main():
    """Main migration function"""
    
    print("\n" + "="*80)
    print("MIGRATION TO 60-CLASS STRUCTURE")
    print("="*80)
    print(f"Started: {datetime.now()}")
    
    try:
        # Step 1: Migrate existing assignments
        migrated = migrate_existing_assignments()
        
        # Step 2: Assign teachers to new classes
        new_assignments = assign_teachers_to_new_classes()
        
        # Step 3: Create sample requests
        sample_requests = create_sample_requests()
        
        # Step 4: Generate statistics
        generate_statistics()
        
        print("\n" + "="*80)
        print("MIGRATION SUMMARY")
        print("="*80)
        print(f"✅ Migrated assignments: {migrated}")
        print(f"✅ New assignments: {new_assignments}")
        print(f"✅ Sample requests: {sample_requests}")
        print(f"✅ Total: {migrated + new_assignments} assignments in 60-class structure")
        
        print("\n📝 Key Changes:")
        print("  - Expanded from 12 to 60 classes")
        print("  - Added Primary School (24 classes)")
        print("  - Added High School grades 11-12 (12 classes)")
        print("  - Organized by categories: PRIMARY, MIDDLE, HIGH")
        print("  - Each category has specialized streams/tracks")
        
        print(f"\n🎯 Ready for Teacher Assessment with 60 classes!")
        print("="*80)
        print(f"Completed: {datetime.now()}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)