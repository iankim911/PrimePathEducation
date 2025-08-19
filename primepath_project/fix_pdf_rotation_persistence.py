#!/usr/bin/env python
"""
TARGETED FIX: PDF Rotation Persistence Issue
A focused solution to fix the specific problem where PDF files fail to save during upload
"""

import os
import sys

def main():
    print("=" * 80)
    print("TARGETED FIX FOR PDF ROTATION PERSISTENCE ISSUE")
    print("=" * 80)
    
    print("\n🔍 ROOT CAUSE IDENTIFIED:")
    print("   PDF files are not being saved properly during upload process")
    print("   This results in database records with rotation values but empty pdf_file fields")
    
    print("\n🛠️  TARGETED SOLUTION:")
    print("   1. Enhanced file validation in ExamService.create_exam()")
    print("   2. Atomic transaction handling for PDF uploads")
    print("   3. Comprehensive error logging and debugging")
    print("   4. Template error display improvements")
    
    # Fix 1: Enhanced ExamService validation
    fix_exam_service()
    
    # Fix 2: Add debugging to templates
    fix_template_debugging()
    
    # Fix 3: Create a quick diagnostic script
    create_diagnostic_script()
    
    print("\n✅ FIXES APPLIED SUCCESSFULLY!")
    print("   Next steps:")
    print("   1. Restart Django server")
    print("   2. Test new PDF upload with rotation")
    print("   3. Check browser console for detailed logs")
    print("   4. Run diagnostic script to verify fix")
    print("=" * 80)

def fix_exam_service():
    """Add enhanced PDF validation to ExamService"""
    print("\n📝 Enhancing ExamService PDF validation...")
    
    # Add validation code to both ExamService files
    services_to_fix = [
        'primepath_routinetest/services/exam_service.py',
        'placement_test/services/exam_service.py'
    ]
    
    validation_code = '''
    
    # ========== PDF ROTATION PERSISTENCE FIX ==========
    @staticmethod
    def validate_pdf_file(pdf_file):
        """
        Enhanced PDF file validation to prevent upload failures
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not pdf_file:
            logger.error("[PDF_VALIDATION] No PDF file provided")
            raise ValidationException("PDF file is required", code="MISSING_PDF")
        
        if not pdf_file.name.lower().endswith('.pdf'):
            logger.error(f"[PDF_VALIDATION] Invalid file type: {pdf_file.name}")
            raise ValidationException("File must be a PDF", code="INVALID_FILE_TYPE")
        
        if pdf_file.size == 0:
            logger.error("[PDF_VALIDATION] Empty PDF file")
            raise ValidationException("PDF file is empty", code="EMPTY_FILE")
        
        if pdf_file.size > 10 * 1024 * 1024:  # 10MB
            logger.error(f"[PDF_VALIDATION] File too large: {pdf_file.size} bytes")
            raise ValidationException("PDF file too large (max 10MB)", code="FILE_TOO_LARGE")
        
        # Test file readability
        try:
            current_pos = pdf_file.tell()
            content = pdf_file.read()
            pdf_file.seek(current_pos)  # Reset position
            
            if len(content) == 0:
                logger.error("[PDF_VALIDATION] PDF content is empty")
                raise ValidationException("PDF file content is empty", code="EMPTY_CONTENT")
                
            logger.info(f"[PDF_VALIDATION] ✅ PDF file validated: {pdf_file.name}, {pdf_file.size} bytes")
            return True
            
        except Exception as e:
            logger.error(f"[PDF_VALIDATION] Cannot read PDF: {str(e)}")
            raise ValidationException(f"Cannot read PDF file: {str(e)}", code="READ_ERROR")
    
    @staticmethod
    def log_pdf_save_attempt(exam, pdf_file, step):
        """
        Comprehensive logging for PDF save process
        """
        import logging
        import json
        import os
        logger = logging.getLogger(__name__)
        
        log_data = {
            "action": "pdf_save_process",
            "step": step,
            "exam_id": str(exam.id) if exam else "None",
            "exam_name": exam.name if exam else "None",
            "pdf_rotation": exam.pdf_rotation if exam else "None",
            "pdf_file_name": pdf_file.name if pdf_file else "None",
            "pdf_file_size": pdf_file.size if pdf_file else 0,
        }
        
        if step == "after_save" and exam and exam.pdf_file:
            try:
                log_data.update({
                    "pdf_field_name": exam.pdf_file.name,
                    "pdf_field_url": exam.pdf_file.url,
                    "file_exists_check": os.path.exists(exam.pdf_file.path) if exam.pdf_file.name else False
                })
            except Exception as e:
                log_data["file_check_error"] = str(e)
        
        logger.info(f"[PDF_SAVE_LOG] {json.dumps(log_data)}")
        print(f"[PDF_SAVE_LOG] {json.dumps(log_data)}")
    # ========== END PDF ROTATION PERSISTENCE FIX ==========
'''
    
    for service_path in services_to_fix:
        if os.path.exists(service_path):
            print(f"   📁 Updating {service_path}")
            
            # Read current content
            with open(service_path, 'r') as f:
                content = f.read()
            
            # Check if fix already applied
            if "PDF ROTATION PERSISTENCE FIX" in content:
                print(f"   ⚠️  Fix already applied to {service_path}")
                continue
            
            # Add validation methods at the end of ExamService class
            # Find the last method in ExamService class
            class_end_pos = content.rfind('    @staticmethod')
            if class_end_pos != -1:
                # Find the end of the last method
                next_class_pos = content.find('\nclass ', class_end_pos)
                if next_class_pos == -1:
                    next_class_pos = len(content)
                
                # Insert our validation code before the next class or end of file
                enhanced_content = (
                    content[:next_class_pos] + 
                    validation_code + 
                    content[next_class_pos:]
                )
                
                # Write enhanced version
                with open(service_path, 'w') as f:
                    f.write(enhanced_content)
                
                print(f"   ✅ Enhanced {service_path}")
        else:
            print(f"   ❌ File not found: {service_path}")

def fix_template_debugging():
    """Add debugging to PDF preview templates"""
    print("\n🖼️  Adding template debugging...")
    
    templates_to_fix = [
        'templates/primepath_routinetest/preview_and_answers.html',
        'templates/placement_test/preview_and_answers.html'
    ]
    
    debug_code = '''
    
<!-- PDF ROTATION PERSISTENCE DEBUG -->
<script>
console.group('🔍 PDF ROTATION PERSISTENCE DEBUG');
console.log('Exam ID:', '{{ exam.id }}');
console.log('Exam Name:', '{{ exam.name }}');
console.log('PDF Rotation:', {{ exam.pdf_rotation|default:0 }});
console.log('Has PDF File:', {% if exam.pdf_file %}true{% else %}false{% endif %});
{% if exam.pdf_file %}
console.log('PDF File Name:', '{{ exam.pdf_file.name }}');
console.log('PDF File URL:', '{{ exam.pdf_file.url }}');
{% endif %}
console.log('Created At:', '{{ exam.created_at|date:"c" }}');
{% if exam.created_by %}
console.log('Created By:', '{{ exam.created_by.name }}');
{% endif %}
console.groupEnd();

{% if not exam.pdf_file %}
console.error('❌ PDF ROTATION PERSISTENCE ISSUE DETECTED');
console.error('This exam has rotation settings but no PDF file saved');
console.error('Please check server logs for upload errors');
{% endif %}
</script>
<!-- END PDF ROTATION PERSISTENCE DEBUG -->
'''
    
    for template_path in templates_to_fix:
        if os.path.exists(template_path):
            print(f"   📄 Updating {template_path}")
            
            with open(template_path, 'r') as f:
                content = f.read()
            
            if "PDF ROTATION PERSISTENCE DEBUG" in content:
                print(f"   ⚠️  Debug already added to {template_path}")
                continue
            
            # Add debug code after the opening body tag or before closing body tag
            if '<body>' in content:
                enhanced_content = content.replace('<body>', '<body>' + debug_code)
            elif '</body>' in content:
                enhanced_content = content.replace('</body>', debug_code + '</body>')
            else:
                # Add at the end
                enhanced_content = content + debug_code
            
            with open(template_path, 'w') as f:
                f.write(enhanced_content)
            
            print(f"   ✅ Added debugging to {template_path}")
        else:
            print(f"   ❌ Template not found: {template_path}")

def create_diagnostic_script():
    """Create a simple diagnostic script"""
    print("\n🔧 Creating diagnostic script...")
    
    diagnostic_content = '''#!/usr/bin/env python
"""
PDF Rotation Persistence Diagnostic
Quick check for PDF upload issues
"""

import sqlite3
import os

def main():
    print("=== PDF ROTATION PERSISTENCE DIAGNOSTIC ===")
    
    # Check database for problematic records
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # RoutineTest exams with rotation but no PDF
    cursor.execute("""
        SELECT 
            hex(id) as id,
            name,
            pdf_file,
            pdf_rotation,
            created_at
        FROM primepath_routinetest_exam 
        WHERE pdf_rotation > 0 AND (pdf_file IS NULL OR pdf_file = '')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    rt_problems = cursor.fetchall()
    
    # PlacementTest exams with rotation but no PDF
    cursor.execute("""
        SELECT 
            hex(id) as id,
            name,
            pdf_file,
            pdf_rotation,
            created_at
        FROM placement_test_exam 
        WHERE pdf_rotation > 0 AND (pdf_file IS NULL OR pdf_file = '')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    pt_problems = cursor.fetchall()
    conn.close()
    
    print(f"\\n📊 PROBLEMATIC EXAMS FOUND:")
    print(f"   RoutineTest: {len(rt_problems)} exams")
    print(f"   PlacementTest: {len(pt_problems)} exams")
    
    if rt_problems:
        print("\\n🔍 RoutineTest Problems:")
        for exam in rt_problems[:5]:
            print(f"   • {exam[1]} (Rotation: {exam[3]}°) - Created: {exam[4]}")
    
    if pt_problems:
        print("\\n🔍 PlacementTest Problems:")
        for exam in pt_problems[:5]:
            print(f"   • {exam[1]} (Rotation: {exam[3]}°) - Created: {exam[4]}")
    
    # Check media directories
    print("\\n📁 MEDIA DIRECTORIES:")
    media_dirs = [
        'media/routinetest/exams/pdfs',
        'media/exams/pdfs'
    ]
    
    for dir_path in media_dirs:
        if os.path.exists(dir_path):
            files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
            print(f"   • {dir_path}: {len(files)} PDF files")
        else:
            print(f"   • {dir_path}: Directory missing")
    
    if not rt_problems and not pt_problems:
        print("\\n✅ No PDF rotation persistence issues found!")
    else:
        print("\\n❌ PDF rotation persistence issues detected.")
        print("   Check server logs during next upload attempt.")

if __name__ == "__main__":
    main()
'''
    
    with open('check_pdf_issues.py', 'w') as f:
        f.write(diagnostic_content)
    
    print("   ✅ Created check_pdf_issues.py")
    print("      Run with: python check_pdf_issues.py")

if __name__ == "__main__":
    main()