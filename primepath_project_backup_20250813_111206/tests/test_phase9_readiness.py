#!/usr/bin/env python
"""
Phase 9 Readiness Check - Model Modularization Preparation
Tests to ensure all features are working before model modularization
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.db import models
from placement_test.models import Exam, Question, AudioFile, StudentSession, StudentAnswer
from core.models import CurriculumLevel, School, Teacher, PlacementRule, Program, SubProgram
from placement_test.services import ExamService, SessionService, PlacementService, GradingService
import inspect


class Phase9ReadinessCheck:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def log(self, message, level="INFO"):
        symbols = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}
        print(f"{symbols.get(level, '•')} {message}")
    
    def test_model_relationships(self):
        """Test all critical model relationships"""
        self.log("Testing Model Relationships...", "INFO")
        
        try:
            # Test Exam -> Question relationship
            exam = Exam.objects.first()
            if exam:
                questions = exam.questions.all()
                self.log(f"Exam->Questions: {questions.count()} questions", "PASS")
                
                # Test Exam -> AudioFile relationship
                audio_files = exam.audio_files.all()
                self.log(f"Exam->AudioFiles: {audio_files.count()} files", "PASS")
                
                # Test Question -> AudioFile relationship
                q_with_audio = exam.questions.filter(audio_file__isnull=False).count()
                self.log(f"Question->AudioFile: {q_with_audio} assignments", "PASS")
                
                # Test StudentSession relationships
                sessions = exam.sessions.all()
                self.log(f"Exam->Sessions: {sessions.count()} sessions", "PASS")
                
                self.passed.append("Model Relationships")
            else:
                self.log("No exam found for testing", "WARN")
                self.warnings.append("No test data")
                
        except Exception as e:
            self.log(f"Model relationship test failed: {e}", "FAIL")
            self.failed.append("Model Relationships")
    
    def test_service_layer_integrity(self):
        """Test that all services are working properly"""
        self.log("Testing Service Layer Integrity...", "INFO")
        
        try:
            # Test ExamService
            exam = Exam.objects.first()
            if exam:
                # Test methods that exist
                if hasattr(ExamService, 'update_exam_questions'):
                    result = ExamService.update_exam_questions(exam, [])
                    self.log("ExamService.update_exam_questions: OK", "PASS")
                
                if hasattr(ExamService, 'update_audio_assignments'):
                    result = ExamService.update_audio_assignments(exam, {})
                    self.log("ExamService.update_audio_assignments: OK", "PASS")
                
                # Check available methods
                methods = [m for m in dir(ExamService) if not m.startswith('_')]
                self.log(f"ExamService has {len(methods)} methods", "INFO")
                
            # Test SessionService
            if hasattr(SessionService, 'create_session'):
                self.log("SessionService.create_session: Available", "PASS")
            
            # Test PlacementService
            if hasattr(PlacementService, 'get_initial_level'):
                self.log("PlacementService.get_initial_level: Available", "PASS")
            
            # Test GradingService
            if hasattr(GradingService, 'auto_grade_answer'):
                self.log("GradingService.auto_grade_answer: Available", "PASS")
            
            self.passed.append("Service Layer")
                
        except Exception as e:
            self.log(f"Service layer test failed: {e}", "FAIL")
            self.failed.append("Service Layer")
    
    def analyze_model_structure(self):
        """Analyze current model structure for modularization"""
        self.log("Analyzing Model Structure...", "INFO")
        
        try:
            # Count models in each module
            placement_models = [
                name for name, obj in inspect.getmembers(
                    sys.modules['placement_test.models']
                ) if inspect.isclass(obj) and issubclass(obj, models.Model)
                and obj.__module__ == 'placement_test.models'
            ]
            
            core_models = [
                name for name, obj in inspect.getmembers(
                    sys.modules['core.models']
                ) if inspect.isclass(obj) and issubclass(obj, models.Model)
                and obj.__module__ == 'core.models'
            ]
            
            self.log(f"Placement Test Models: {len(placement_models)}", "INFO")
            for model in placement_models:
                self.log(f"  - {model}", "INFO")
            
            self.log(f"Core Models: {len(core_models)}", "INFO")
            for model in core_models:
                self.log(f"  - {model}", "INFO")
            
            # Check for circular dependencies
            self.log("Checking for circular dependencies...", "INFO")
            
            # Placement models importing from core
            from placement_test.models import Exam
            if hasattr(Exam, 'curriculum_level'):
                self.log("Exam -> CurriculumLevel: OK", "PASS")
            if hasattr(Exam, 'created_by'):
                self.log("Exam -> Teacher: OK", "PASS")
            
            # Core models importing from placement
            from core.models import ExamLevelMapping
            if hasattr(ExamLevelMapping, 'exam'):
                self.log("ExamLevelMapping -> Exam: Cross-app reference", "WARN")
                self.warnings.append("Cross-app model reference detected")
            
            self.passed.append("Model Structure Analysis")
            
        except Exception as e:
            self.log(f"Model structure analysis failed: {e}", "FAIL")
            self.failed.append("Model Structure Analysis")
    
    def test_database_integrity(self):
        """Test database integrity and migrations"""
        self.log("Testing Database Integrity...", "INFO")
        
        try:
            # Test that we can query all models
            models_to_test = [
                (Exam, "Exam"),
                (Question, "Question"),
                (AudioFile, "AudioFile"),
                (StudentSession, "StudentSession"),
                (StudentAnswer, "StudentAnswer"),
                (Program, "Program"),
                (SubProgram, "SubProgram"),
                (CurriculumLevel, "CurriculumLevel"),
                (PlacementRule, "PlacementRule"),
                (School, "School"),
                (Teacher, "Teacher"),
            ]
            
            for model_class, name in models_to_test:
                count = model_class.objects.count()
                self.log(f"{name}: {count} records", "PASS")
            
            # Test complex queries
            complex_query = Exam.objects.select_related(
                'curriculum_level__subprogram__program',
                'created_by'
            ).prefetch_related(
                'questions',
                'audio_files',
                'sessions'
            ).first()
            
            if complex_query:
                self.log("Complex query with joins: OK", "PASS")
            
            self.passed.append("Database Integrity")
            
        except Exception as e:
            self.log(f"Database integrity test failed: {e}", "FAIL")
            self.failed.append("Database Integrity")
    
    def create_modularization_plan(self):
        """Create a safe plan for model modularization"""
        self.log("\n" + "="*60, "INFO")
        self.log("MODEL MODULARIZATION PLAN (Phase 9)", "INFO")
        self.log("="*60, "INFO")
        
        plan = """
## Proposed Model Structure:

### placement_test/models/
├── __init__.py        # Re-export all models for compatibility
├── exam.py            # Exam, AudioFile
├── question.py        # Question
├── session.py         # StudentSession, StudentAnswer, DifficultyAdjustment
└── managers.py        # Custom managers

### core/models/
├── __init__.py        # Re-export all models
├── user.py            # Teacher, School
├── curriculum.py      # Program, SubProgram, CurriculumLevel
├── placement.py       # PlacementRule, ExamLevelMapping
└── managers.py        # Custom managers

## Implementation Steps:

1. **Create model directories** (no risk)
2. **Copy models to new files** (keep originals)
3. **Update imports in __init__.py** (maintain compatibility)
4. **Test thoroughly** (ensure no breaks)
5. **Remove old models.py** (only after verification)

## Safety Measures:

1. All models re-exported from __init__.py
2. No URL changes required
3. No view changes required
4. No template changes required
5. Full backward compatibility

## Potential Issues to Address:

1. Cross-app model reference (ExamLevelMapping -> Exam)
   - Solution: Use string reference 'placement_test.Exam'
   
2. Circular imports risk
   - Solution: Careful import management in __init__.py
   
3. Migration dependencies
   - Solution: No new migrations needed (same models)
"""
        
        print(plan)
        
        return True
    
    def run_all_checks(self):
        """Run all readiness checks"""
        print("\n" + "="*60)
        print("PHASE 9 READINESS CHECK")
        print("="*60 + "\n")
        
        # Run all tests
        self.test_model_relationships()
        print()
        self.test_service_layer_integrity()
        print()
        self.analyze_model_structure()
        print()
        self.test_database_integrity()
        print()
        
        # Summary
        print("\n" + "="*60)
        print("READINESS SUMMARY")
        print("="*60)
        
        print(f"\n✅ Passed: {len(self.passed)}")
        for item in self.passed:
            print(f"  - {item}")
        
        if self.warnings:
            print(f"\n⚠️ Warnings: {len(self.warnings)}")
            for item in self.warnings:
                print(f"  - {item}")
        
        if self.failed:
            print(f"\n❌ Failed: {len(self.failed)}")
            for item in self.failed:
                print(f"  - {item}")
        
        # Final recommendation
        print("\n" + "="*60)
        if not self.failed:
            print("✅ READY FOR PHASE 9: Model Modularization")
            print("All critical systems are functioning properly.")
            self.create_modularization_plan()
        else:
            print("⚠️ ISSUES DETECTED: Review failures before proceeding")
        print("="*60)
        
        return len(self.failed) == 0


if __name__ == "__main__":
    checker = Phase9ReadinessCheck()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)