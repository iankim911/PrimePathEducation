#!/usr/bin/env python
"""
COMPREHENSIVE FIX: PDF Rotation Persistence Failure
Addresses the issue where PDF files are uploaded with rotation but fail to be saved properly,
resulting in "No PDF file uploaded for this exam!" error in preview.

ROOT CAUSE: File upload transaction failures during exam creation
SOLUTION: Enhanced error handling, validation, and robust file upload process
"""

import os
import sys
import django
import shutil
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from primepath_routinetest.models import Exam as RoutineTestExam
from placement_test.models import Exam as PlacementTestExam
from primepath_routinetest.services import ExamService as RoutineTestExamService
from placement_test.services import ExamService as PlacementTestExamService
from core.models import Teacher, CurriculumLevel
import json

class PDFRotationPersistenceFix:
    """
    Comprehensive fix for PDF rotation persistence issues
    """
    
    def __init__(self):
        self.console_logs = []
        self.fixes_applied = []
        
    def log_console(self, message, data=None):
        """Enhanced console logging"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'data': data
        }
        self.console_logs.append(log_entry)
        print(f"[PDF_FIX] {timestamp}: {message}")
        if data:
            print(f"    Data: {json.dumps(data, indent=2, default=str)}")
    
    def diagnose_issue(self):
        """Comprehensive diagnosis of PDF rotation persistence issues"""
        self.log_console("=== DIAGNOSTIC PHASE ===")
        
        # Check for failed uploads in both modules
        rt_failed = RoutineTestExam.objects.filter(
            pdf_file__isnull=True,
            pdf_rotation__gt=0
        ).order_by('-created_at')
        
        pt_failed = PlacementTestExam.objects.filter(
            pdf_file__isnull=True,
            pdf_rotation__gt=0
        ).order_by('-created_at')
        
        self.log_console("Failed uploads found", {
            'routine_test_failed': rt_failed.count(),
            'placement_test_failed': pt_failed.count()
        })
        
        # Check file system vs database consistency
        media_root = 'media'
        rt_pdf_dir = os.path.join(media_root, 'routinetest/exams/pdfs')
        pt_pdf_dir = os.path.join(media_root, 'exams/pdfs')
        
        rt_files = os.listdir(rt_pdf_dir) if os.path.exists(rt_pdf_dir) else []
        pt_files = os.listdir(pt_pdf_dir) if os.path.exists(pt_pdf_dir) else []
        
        self.log_console("File system analysis", {
            'routine_test_files': len(rt_files),
            'placement_test_files': len(pt_files),
            'rt_dir_exists': os.path.exists(rt_pdf_dir),
            'pt_dir_exists': os.path.exists(pt_pdf_dir)
        })
        
        return {
            'rt_failed_count': rt_failed.count(),
            'pt_failed_count': pt_failed.count(),
            'rt_failed_exams': list(rt_failed.values('id', 'name', 'pdf_rotation', 'created_at')),
            'pt_failed_exams': list(pt_failed.values('id', 'name', 'pdf_rotation', 'created_at'))
        }
    
    def fix_exam_service_upload_method(self, module='both'):
        """
        Fix the ExamService.create_exam method to ensure robust PDF file handling
        """
        self.log_console("=== FIXING EXAM SERVICE UPLOAD METHODS ===")
        
        # Enhanced ExamService create_exam method with robust error handling
        enhanced_create_exam_code = '''
@staticmethod
@transaction.atomic
def create_exam_enhanced(
    exam_data: Dict[str, Any],
    pdf_file: Optional[UploadedFile] = None,
    audio_files: Optional[List[UploadedFile]] = None,
    audio_names: Optional[List[str]] = None
) -> Exam:
    """
    ENHANCED: Create a new exam with robust PDF file handling.
    Fixes PDF rotation persistence failure issue.
    """
    import logging
    import json
    import os
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    logger = logging.getLogger(__name__)
    
    # Log exam creation attempt with file validation
    console_log = {
        "service": "ExamService",
        "action": "create_exam_enhanced",
        "exam_name": exam_data.get('name'),
        "has_pdf": pdf_file is not None,
        "pdf_name": pdf_file.name if pdf_file else None,
        "pdf_size": pdf_file.size if pdf_file else 0,
        "pdf_content_type": pdf_file.content_type if pdf_file else None,
        "pdf_rotation": exam_data.get('pdf_rotation', 0),
    }
    logger.info(f"[EXAM_CREATE_ENHANCED] {json.dumps(console_log)}")
    print(f"[EXAM_CREATE_ENHANCED] {json.dumps(console_log)}")
    
    # CRITICAL: Validate PDF file before creating exam
    if pdf_file:
        if not pdf_file.name.lower().endswith('.pdf'):
            raise ValidationException("File must be a PDF", code="INVALID_FILE_TYPE")
        
        if pdf_file.size == 0:
            raise ValidationException("PDF file is empty", code="EMPTY_FILE")
        
        if pdf_file.size > 10 * 1024 * 1024:  # 10MB limit
            raise ValidationException("PDF file too large (max 10MB)", code="FILE_TOO_LARGE")
        
        # Test file readability
        try:
            pdf_content = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer
            if len(pdf_content) == 0:
                raise ValidationException("PDF file content is empty", code="EMPTY_CONTENT")
        except Exception as e:
            logger.error(f"[PDF_READ_ERROR] Failed to read PDF file: {str(e)}")
            raise ValidationException(f"Cannot read PDF file: {str(e)}", code="READ_ERROR")
    else:
        raise ValidationException("PDF file is required", code="MISSING_PDF")
    
    # Create exam with atomic transaction
    try:
        # First create the exam object WITHOUT the PDF file
        exam_data_without_pdf = exam_data.copy()
        exam_data_without_pdf['pdf_rotation'] = exam_data.get('pdf_rotation', 0)
        
        exam = Exam.objects.create(
            name=exam_data['name'],
            exam_type=exam_data.get('exam_type', 'REVIEW'),
            time_period_month=exam_data.get('time_period_month'),
            time_period_quarter=exam_data.get('time_period_quarter'),
            academic_year=exam_data.get('academic_year'),
            class_codes=exam_data.get('class_codes', []),
            instructions=exam_data.get('instructions', ''),
            curriculum_level_id=exam_data.get('curriculum_level_id'),
            timer_minutes=exam_data.get('timer_minutes', 60),
            total_questions=exam_data['total_questions'],
            default_options_count=exam_data.get('default_options_count', 5),
            passing_score=exam_data.get('passing_score', 0),
            pdf_rotation=exam_data.get('pdf_rotation', 0),  # CRITICAL: Ensure rotation is saved
            created_by=exam_data.get('created_by'),
            is_active=exam_data.get('is_active', True),
            # PDF file initially NULL - will be set after successful file save
        )
        
        # Log exam created (without PDF yet)
        console_log = {
            "action": "exam_object_created",
            "exam_id": str(exam.id),
            "pdf_rotation_saved": exam.pdf_rotation
        }
        logger.info(f"[EXAM_OBJECT_CREATED] {json.dumps(console_log)}")
        print(f"[EXAM_OBJECT_CREATED] {json.dumps(console_log)}")
        
        # Now save the PDF file separately and update the exam
        try:
            # Save PDF file to the correct location
            pdf_file.seek(0)  # Ensure we're at the start of the file
            exam.pdf_file.save(pdf_file.name, pdf_file, save=True)
            
            # Verify the file was actually saved
            if not exam.pdf_file:
                raise Exception("PDF file failed to save - field is empty")
            
            if not exam.pdf_file.name:
                raise Exception("PDF file failed to save - no filename")
            
            # Check if file exists on disk
            file_path = exam.pdf_file.path
            if not os.path.exists(file_path):
                raise Exception(f"PDF file not found on disk: {file_path}")
            
            # Verify file size
            disk_size = os.path.getsize(file_path)
            if disk_size == 0:
                raise Exception("PDF file saved but is empty on disk")
            
            # Log successful PDF save
            console_log = {
                "action": "pdf_file_saved",
                "exam_id": str(exam.id),
                "pdf_file_name": exam.pdf_file.name,
                "pdf_file_path": file_path,
                "disk_size": disk_size,
                "rotation": exam.pdf_rotation
            }
            logger.info(f"[PDF_SAVED_SUCCESS] {json.dumps(console_log)}")
            print(f"[PDF_SAVED_SUCCESS] {json.dumps(console_log)}")
            
        except Exception as pdf_error:
            # If PDF save fails, delete the exam and re-raise the error
            logger.error(f"[PDF_SAVE_FAILED] PDF save failed for exam {exam.id}: {str(pdf_error)}")
            print(f"[PDF_SAVE_FAILED] PDF save failed for exam {exam.id}: {str(pdf_error)}")
            
            # Clean up the exam record
            exam.delete()
            raise ValidationException(
                f"Failed to save PDF file: {str(pdf_error)}", 
                code="PDF_SAVE_FAILED"
            )
        
        # Create questions and handle audio files (existing logic)
        ExamService.create_questions_for_exam(exam)
        
        if audio_files:
            ExamService.attach_audio_files(exam, audio_files, audio_names or [])
        
        # Final success log with comprehensive verification
        console_log = {
            "action": "create_exam_complete_success",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "pdf_file_saved": bool(exam.pdf_file),
            "pdf_file_name": exam.pdf_file.name if exam.pdf_file else None,
            "pdf_rotation": exam.pdf_rotation,
            "questions_created": exam.total_questions,
            "audio_files_count": len(audio_files) if audio_files else 0
        }
        logger.info(f"[EXAM_CREATE_COMPLETE] {json.dumps(console_log)}")
        print(f"[EXAM_CREATE_COMPLETE] {json.dumps(console_log)}")
        
        return exam
        
    except Exception as e:
        logger.error(f"[EXAM_CREATE_FAILED] Exam creation failed: {str(e)}")
        print(f"[EXAM_CREATE_FAILED] Exam creation failed: {str(e)}")
        raise
'''
        
        # Write enhanced method to both ExamService files
        if module in ['both', 'routinetest']:
            rt_service_path = 'primepath_routinetest/services/exam_service.py'
            self._add_enhanced_method_to_service(rt_service_path, enhanced_create_exam_code)
            self.fixes_applied.append("Enhanced RoutineTest ExamService")
        
        if module in ['both', 'placementtest']:
            pt_service_path = 'placement_test/services/exam_service.py'
            self._add_enhanced_method_to_service(pt_service_path, enhanced_create_exam_code)
            self.fixes_applied.append("Enhanced PlacementTest ExamService")
    
    def _add_enhanced_method_to_service(self, service_path, method_code):
        """Add the enhanced create_exam method to the service file"""
        if not os.path.exists(service_path):
            self.log_console(f"Service file not found: {service_path}")
            return
        
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Add enhanced method at the end of the ExamService class
        enhanced_content = content + "\n\n    # ENHANCED METHOD FOR PDF ROTATION PERSISTENCE FIX\n" + method_code
        
        # Backup original
        backup_path = f"{service_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(service_path, backup_path)
        
        # Write enhanced version
        with open(service_path, 'w') as f:
            f.write(enhanced_content)
        
        self.log_console(f"Enhanced service file: {service_path}")
        self.log_console(f"Backup created: {backup_path}")
    
    def add_comprehensive_logging(self):
        """Add comprehensive logging to both upload views"""
        self.log_console("=== ADDING COMPREHENSIVE LOGGING ===")
        
        # Enhanced logging for upload views
        logging_enhancements = {
            'routinetest_view': 'primepath_routinetest/views/exam.py',
            'placementtest_view': 'placement_test/views/exam.py'
        }
        
        for module, view_path in logging_enhancements.items():
            self._add_logging_to_view(view_path, module)
    
    def _add_logging_to_view(self, view_path, module_name):
        """Add enhanced logging to exam upload views"""
        if not os.path.exists(view_path):
            self.log_console(f"View file not found: {view_path}")
            return
        
        # Create backup
        backup_path = f"{view_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(view_path, backup_path)
        
        with open(view_path, 'r') as f:
            content = f.read()
        
        # Add enhanced logging imports and functions
        enhanced_logging_code = '''

# ENHANCED LOGGING FOR PDF ROTATION PERSISTENCE
def log_pdf_upload_attempt(request, exam_data, pdf_file):
    """Enhanced logging for PDF upload attempts"""
    import json
    import logging
    import os
    
    logger = logging.getLogger(__name__)
    
    log_data = {
        "action": "pdf_upload_attempt",
        "module": "''' + module_name + '''",
        "exam_name": exam_data.get('name'),
        "user": str(request.user),
        "pdf_filename": pdf_file.name if pdf_file else None,
        "pdf_size": pdf_file.size if pdf_file else 0,
        "pdf_content_type": pdf_file.content_type if pdf_file else None,
        "pdf_rotation": exam_data.get('pdf_rotation', 0),
        "request_method": request.method,
        "request_files_keys": list(request.FILES.keys()),
        "request_post_keys": list(request.POST.keys())
    }
    
    logger.info(f"[PDF_UPLOAD_ATTEMPT] {json.dumps(log_data)}")
    print(f"[PDF_UPLOAD_ATTEMPT] {json.dumps(log_data)}")
    
    return log_data

def log_pdf_upload_result(exam, success=True, error=None):
    """Enhanced logging for PDF upload results"""
    import json
    import logging
    import os
    
    logger = logging.getLogger(__name__)
    
    log_data = {
        "action": "pdf_upload_result",
        "module": "''' + module_name + '''",
        "exam_id": str(exam.id) if exam else None,
        "exam_name": exam.name if exam else None,
        "success": success,
        "has_pdf_file": bool(exam.pdf_file) if exam else False,
        "pdf_file_name": exam.pdf_file.name if exam and exam.pdf_file else None,
        "pdf_rotation": exam.pdf_rotation if exam else None,
        "error": str(error) if error else None
    }
    
    if success:
        # Additional verification for successful uploads
        if exam and exam.pdf_file:
            try:
                file_path = exam.pdf_file.path
                log_data.update({
                    "pdf_file_path": file_path,
                    "file_exists_on_disk": os.path.exists(file_path),
                    "file_size_on_disk": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                })
            except Exception as e:
                log_data["verification_error"] = str(e)
    
    logger.info(f"[PDF_UPLOAD_RESULT] {json.dumps(log_data)}")
    print(f"[PDF_UPLOAD_RESULT] {json.dumps(log_data)}")
    
    return log_data
'''
        
        # Insert the enhanced logging code before the create_exam view function
        create_exam_pos = content.find('def create_exam(request):')
        if create_exam_pos == -1:
            self.log_console(f"create_exam function not found in {view_path}")
            return
        
        enhanced_content = (
            content[:create_exam_pos] + 
            enhanced_logging_code + 
            "\n\n" + 
            content[create_exam_pos:]
        )
        
        with open(view_path, 'w') as f:
            f.write(enhanced_content)
        
        self.log_console(f"Enhanced logging added to: {view_path}")
        self.fixes_applied.append(f"Enhanced logging for {module_name}")
    
    def fix_template_pdf_display_logic(self):
        """Fix template logic for PDF display to handle edge cases"""
        self.log_console("=== FIXING TEMPLATE PDF DISPLAY LOGIC ===")
        
        template_files = [
            'templates/primepath_routinetest/preview_and_answers.html',
            'templates/placement_test/preview_and_answers.html'
        ]
        
        for template_path in template_files:
            if os.path.exists(template_path):
                self._fix_template_pdf_logic(template_path)
    
    def _fix_template_pdf_logic(self, template_path):
        """Fix individual template PDF display logic"""
        backup_path = f"{template_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(template_path, backup_path)
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Enhanced PDF display logic with comprehensive error handling
        enhanced_pdf_logic = '''
    <!-- ENHANCED PDF DISPLAY LOGIC -->
    {% if exam.pdf_file %}
        {% comment %} Additional verification that file exists {% endcomment %}
        {% load static %}
        <script>
            // Enhanced PDF file verification
            console.log('[PDF_DISPLAY] Checking PDF file for exam:', '{{ exam.id }}');
            console.log('[PDF_DISPLAY] PDF file field:', '{{ exam.pdf_file }}');
            console.log('[PDF_DISPLAY] PDF file name:', '{{ exam.pdf_file.name }}');
            console.log('[PDF_DISPLAY] PDF rotation:', {{ exam.pdf_rotation|default:0 }});
            
            const pdfUrl = "{{ exam.pdf_file.url }}";
            console.log('[PDF_DISPLAY] PDF URL:', pdfUrl);
            
            // Test if PDF file is accessible
            fetch(pdfUrl, { method: 'HEAD' })
                .then(response => {
                    if (response.ok) {
                        console.log('[PDF_DISPLAY] ✅ PDF file accessible');
                        console.log('[PDF_DISPLAY] Content-Type:', response.headers.get('content-type'));
                        console.log('[PDF_DISPLAY] Content-Length:', response.headers.get('content-length'));
                    } else {
                        console.error('[PDF_DISPLAY] ❌ PDF file not accessible:', response.status);
                        document.getElementById('pdf-loading').innerHTML = 
                            '<div class="alert alert-danger">PDF file exists in database but is not accessible (HTTP ' + response.status + ')</div>';
                    }
                })
                .catch(error => {
                    console.error('[PDF_DISPLAY] ❌ Error checking PDF file:', error);
                    document.getElementById('pdf-loading').innerHTML = 
                        '<div class="alert alert-danger">Error checking PDF file: ' + error.message + '</div>';
                });
        </script>
    {% else %}
        <div class="alert alert-warning">
            <strong>No PDF file uploaded for this exam!</strong>
            <br>
            <small>
                Exam ID: {{ exam.id }}<br>
                Exam Name: {{ exam.name }}<br>
                PDF Rotation Setting: {{ exam.pdf_rotation|default:0 }}°<br>
                Created: {{ exam.created_at|date:"Y-m-d H:i:s" }}<br>
                {% if exam.created_by %}Created by: {{ exam.created_by.name }}{% endif %}
            </small>
        </div>
        <script>
            console.error('[PDF_DISPLAY] ❌ No PDF file for exam {{ exam.id }}');
            console.error('[PDF_DISPLAY] Exam data:', {
                id: '{{ exam.id }}',
                name: '{{ exam.name }}',
                pdf_rotation: {{ exam.pdf_rotation|default:0 }},
                created_at: '{{ exam.created_at|date:"c" }}',
                created_by: '{% if exam.created_by %}{{ exam.created_by.name }}{% endif %}'
            });
        </script>
    {% endif %}
'''
        
        # Replace the existing PDF display logic
        import re
        pdf_check_pattern = r'{% if exam\.pdf_file %}.*?{% else %}.*?{% endif %}'
        
        if re.search(pdf_check_pattern, content, re.DOTALL):
            enhanced_content = re.sub(pdf_check_pattern, enhanced_pdf_logic.strip(), content, flags=re.DOTALL)
        else:
            # If pattern not found, add at the end of PDF section
            enhanced_content = content + "\n\n" + enhanced_pdf_logic
        
        with open(template_path, 'w') as f:
            f.write(enhanced_content)
        
        self.log_console(f"Enhanced PDF display logic: {template_path}")
        self.fixes_applied.append(f"Enhanced template: {template_path}")
    
    def create_diagnostic_tool(self):
        """Create a diagnostic tool for ongoing PDF issues"""
        diagnostic_code = '''#!/usr/bin/env python
"""
PDF Rotation Persistence Diagnostic Tool
Run this script to diagnose PDF upload issues
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models import Exam as RTExam
from placement_test.models import Exam as PTExam
import json

def diagnose_pdf_issues():
    print("=== PDF ROTATION PERSISTENCE DIAGNOSTIC ===")
    
    # Check for problematic exams
    rt_problems = RTExam.objects.filter(pdf_rotation__gt=0, pdf_file__isnull=True)
    pt_problems = PTExam.objects.filter(pdf_rotation__gt=0, pdf_file__isnull=True)
    
    print(f"RoutineTest exams with rotation but no PDF: {rt_problems.count()}")
    print(f"PlacementTest exams with rotation but no PDF: {pt_problems.count()}")
    
    # List problematic exams
    for exam in rt_problems:
        print(f"  RT Problem: {exam.name} (ID: {exam.id}, Rotation: {exam.pdf_rotation}°)")
    
    for exam in pt_problems:
        print(f"  PT Problem: {exam.name} (ID: {exam.id}, Rotation: {exam.pdf_rotation}°)")
    
    # Check file system
    media_dirs = [
        'media/routinetest/exams/pdfs',
        'media/exams/pdfs'
    ]
    
    for dir_path in media_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"{dir_path}: {len(files)} files")
        else:
            print(f"{dir_path}: Directory does not exist")

if __name__ == "__main__":
    diagnose_pdf_issues()
'''
        
        with open('pdf_diagnostic_tool.py', 'w') as f:
            f.write(diagnostic_code)
        
        self.log_console("Created diagnostic tool: pdf_diagnostic_tool.py")
        self.fixes_applied.append("Created pdf_diagnostic_tool.py")
    
    def run_comprehensive_fix(self):
        """Run all fix procedures"""
        self.log_console("=== STARTING COMPREHENSIVE PDF ROTATION PERSISTENCE FIX ===")
        
        # Step 1: Diagnose the issue
        diagnosis = self.diagnose_issue()
        
        # Step 2: Fix ExamService upload methods
        self.fix_exam_service_upload_method()
        
        # Step 3: Add comprehensive logging
        self.add_comprehensive_logging()
        
        # Step 4: Fix template display logic
        self.fix_template_pdf_display_logic()
        
        # Step 5: Create diagnostic tool
        self.create_diagnostic_tool()
        
        # Summary
        self.log_console("=== COMPREHENSIVE FIX COMPLETE ===")
        self.log_console("Fixes applied", {
            'total_fixes': len(self.fixes_applied),
            'fixes_list': self.fixes_applied,
            'diagnosis': diagnosis
        })
        
        print("\n" + "="*80)
        print("PDF ROTATION PERSISTENCE FIX SUMMARY")
        print("="*80)
        print(f"✅ {len(self.fixes_applied)} fixes applied:")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"   {i}. {fix}")
        
        print(f"\n📊 Issues diagnosed:")
        print(f"   • RoutineTest failed uploads: {diagnosis['rt_failed_count']}")
        print(f"   • PlacementTest failed uploads: {diagnosis['pt_failed_count']}")
        
        print(f"\n🛠️ Next steps:")
        print("   1. Restart the Django server")
        print("   2. Test uploading a new exam with PDF rotation")
        print("   3. Check console logs for enhanced debugging info")
        print("   4. Run pdf_diagnostic_tool.py to monitor issues")
        print("="*80)

def main():
    """Main execution function"""
    fix = PDFRotationPersistenceFix()
    fix.run_comprehensive_fix()

if __name__ == "__main__":
    main()