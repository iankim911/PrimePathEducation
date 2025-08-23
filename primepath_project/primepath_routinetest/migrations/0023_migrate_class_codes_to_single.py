# Data migration to transfer from class_codes array to single class_code field
# Date: 2025-08-23

from django.db import migrations
import logging

logger = logging.getLogger(__name__)

def migrate_to_single_class_code(apps, schema_editor):
    """
    Migrate from class_codes (JSONField array) to class_code (single CharField)
    """
    Exam = apps.get_model('primepath_routinetest', 'Exam')
    db_alias = schema_editor.connection.alias
    
    migrated_count = 0
    error_count = 0
    
    logger.info("[MIGRATION] Starting migration from class_codes to class_code field")
    
    for exam in Exam.objects.using(db_alias).all():
        try:
            if exam.class_codes:
                if isinstance(exam.class_codes, list):
                    if len(exam.class_codes) == 1:
                        # Single class - migrate directly
                        exam.class_code = exam.class_codes[0]
                        exam.save()
                        migrated_count += 1
                        logger.info(f"[MIGRATION] Exam {exam.id} migrated to class_code: {exam.class_code}")
                    elif len(exam.class_codes) > 1:
                        # Multiple classes - should have been split in previous migration
                        logger.error(f"[MIGRATION] ERROR: Exam {exam.id} still has multiple classes: {exam.class_codes}")
                        # Take first class as fallback
                        exam.class_code = exam.class_codes[0]
                        exam.save()
                        error_count += 1
                    else:
                        # Empty list
                        exam.class_code = None
                        exam.save()
                        logger.info(f"[MIGRATION] Exam {exam.id} has empty class_codes, set class_code to None")
                elif isinstance(exam.class_codes, str):
                    # String value - migrate directly
                    exam.class_code = exam.class_codes
                    exam.save()
                    migrated_count += 1
                    logger.info(f"[MIGRATION] Exam {exam.id} migrated string class_code: {exam.class_code}")
            else:
                # No class codes
                exam.class_code = None
                exam.save()
                logger.info(f"[MIGRATION] Exam {exam.id} has no class_codes, set class_code to None")
                
        except Exception as e:
            logger.error(f"[MIGRATION] Error migrating exam {exam.id}: {e}")
            error_count += 1
    
    logger.info(f"[MIGRATION] Migration complete: {migrated_count} successful, {error_count} errors")
    
    # Verification check
    verify_count = 0
    for exam in Exam.objects.using(db_alias).all():
        if exam.class_codes and isinstance(exam.class_codes, list) and len(exam.class_codes) > 1:
            verify_count += 1
            logger.error(f"[MIGRATION] VERIFICATION FAILED: Exam {exam.id} still has multiple classes!")
    
    if verify_count == 0:
        logger.info("[MIGRATION] ✅ VERIFICATION PASSED: All exams have single class or none")
    else:
        logger.error(f"[MIGRATION] ❌ VERIFICATION FAILED: {verify_count} exams still have multiple classes")

def reverse_migrate(apps, schema_editor):
    """
    Reverse migration - copy class_code back to class_codes as single-item array
    """
    Exam = apps.get_model('primepath_routinetest', 'Exam')
    db_alias = schema_editor.connection.alias
    
    for exam in Exam.objects.using(db_alias).all():
        if exam.class_code:
            exam.class_codes = [exam.class_code]
        else:
            exam.class_codes = []
        exam.save()
    
    logger.info("[MIGRATION] Reversed migration from class_code to class_codes")

class Migration(migrations.Migration):
    
    dependencies = [
        ('primepath_routinetest', '0022_fix_exam_class_relationship'),
    ]
    
    operations = [
        migrations.RunPython(
            migrate_to_single_class_code,
            reverse_migrate,
            hints={'model_name': 'exam'}
        ),
    ]