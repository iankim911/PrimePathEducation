"""
API Views - Phase 8
RESTful API endpoints using Django REST Framework
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from placement_test.models import (
    Exam, Question, AudioFile, StudentSession, StudentAnswer
)
from core.models import (
    School, Program, SubProgram, CurriculumLevel
)
from placement_test.services import (
    PlacementService, SessionService, ExamService, GradingService
)
from core.services import DashboardService, FileService
from core.cache_service import cache_result, CacheService
from core.monitoring_service import MetricsCollector, ActivityLogger

from .serializers import (
    ExamSerializer, ExamDetailSerializer, QuestionSerializer,
    StudentSessionSerializer, StudentSessionDetailSerializer,
    StudentAnswerSerializer, SchoolSerializer, ProgramSerializer,
    StartTestSerializer, SubmitAnswerSerializer,
    BatchAnswerSerializer, SessionStatusSerializer, TestResultSerializer,
    DashboardStatsSerializer, ExamStatisticsSerializer
)
from ..common.permissions import IsTeacherOrReadOnly, IsOwnerOrTeacher
from ..common.pagination import StandardResultsSetPagination
from .filters import ExamFilter, SessionFilter

import logging

logger = logging.getLogger(__name__)


# Base ViewSets

class ExamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Exam CRUD operations.
    
    Endpoints:
    - GET /api/v1/exams/ - List all exams
    - POST /api/v1/exams/ - Create new exam
    - GET /api/v1/exams/{id}/ - Get exam details
    - PUT /api/v1/exams/{id}/ - Update exam
    - DELETE /api/v1/exams/{id}/ - Delete exam
    - GET /api/v1/exams/{id}/questions/ - Get exam questions
    - POST /api/v1/exams/{id}/upload-pdf/ - Upload PDF
    - GET /api/v1/exams/{id}/statistics/ - Get exam statistics
    """
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsTeacherOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filterset_class = ExamFilter
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return ExamDetailSerializer
        return ExamSerializer
    
    def get_queryset(self):
        """Optimize queryset based on action."""
        queryset = super().get_queryset()
        
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'questions__options',
                'questions__audio_file',
                'audio_files'
            )
        elif self.action == 'list':
            queryset = queryset.select_related('curriculum_level')
            
        # Filter active exams for students
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get paginated questions for an exam."""
        exam = self.get_object()
        questions = exam.questions.all().order_by('question_number')
        
        page = self.paginate_queryset(questions)
        if page is not None:
            serializer = QuestionSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = QuestionSerializer(questions, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_pdf(self, request, pk=None):
        """Upload PDF file for exam."""
        exam = self.get_object()
        
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pdf_file = request.FILES['file']
            pdf_info = FileService.save_exam_pdf(pdf_file, exam.id)
            
            # Update exam with PDF info
            exam.pdf_file = pdf_info['path']
            exam.save()
            
            ActivityLogger.log_user_action(
                user_id=request.user.id,
                action='upload_exam_pdf',
                details={'exam_id': str(exam.id), 'file_size': pdf_info.get('size')}
            )
            
            return Response({
                'success': True,
                'pdf_url': request.build_absolute_uri(exam.pdf_file.url)
            })
            
        except Exception as e:
            logger.error(f"PDF upload failed: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    @cache_result(prefix='exam_stats', timeout=300)
    def statistics(self, request, pk=None):
        """Get statistics for an exam."""
        exam = self.get_object()
        
        stats = ExamService.get_exam_statistics(exam.id)
        serializer = ExamStatisticsSerializer(stats)
        
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Log exam creation."""
        exam = serializer.save()
        ActivityLogger.log_user_action(
            user_id=self.request.user.id,
            action='create_exam',
            details={'exam_id': str(exam.id), 'exam_name': exam.name}
        )
        CacheService.clear_dashboard_cache()
    
    def perform_destroy(self, instance):
        """Clean up files when deleting exam."""
        exam_id = instance.id
        
        # Delete associated files
        if instance.pdf_file:
            FileService.delete_file(instance.pdf_file.name)
        
        # Clear cache
        CacheService.clear_exam_cache(str(exam_id))
        
        # Log deletion
        ActivityLogger.log_user_action(
            user_id=self.request.user.id,
            action='delete_exam',
            details={'exam_id': str(exam_id), 'exam_name': instance.name}
        )
        
        instance.delete()


class StudentSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StudentSession operations.
    
    Endpoints:
    - GET /api/v1/sessions/ - List sessions
    - POST /api/v1/sessions/ - Start new session
    - GET /api/v1/sessions/{id}/ - Get session details
    - POST /api/v1/sessions/{id}/submit-answer/ - Submit single answer
    - POST /api/v1/sessions/{id}/submit-batch/ - Submit multiple answers
    - POST /api/v1/sessions/{id}/complete/ - Complete session
    - GET /api/v1/sessions/{id}/status/ - Get session status
    """
    queryset = StudentSession.objects.all()
    serializer_class = StudentSessionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filterset_class = SessionFilter
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return StudentSessionDetailSerializer
        return StudentSessionSerializer
    
    def get_queryset(self):
        """Optimize queryset and filter based on user."""
        queryset = super().get_queryset()
        
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'answers__question',
                'exam__questions'
            )
        else:
            queryset = queryset.select_related(
                'exam', 'school', 'final_curriculum_level'
            )
        
        # Filter for non-staff users
        if not self.request.user.is_staff:
            # Students can only see their own sessions (by session ID in request)
            session_id = self.request.session.get('session_id')
            if session_id:
                queryset = queryset.filter(id=session_id)
            else:
                queryset = queryset.none()
        
        return queryset.order_by('-started_at')
    
    def create(self, request, *args, **kwargs):
        """Start a new test session."""
        serializer = StartTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Use PlacementService to match student to exam
            exam, curriculum_level = PlacementService.match_student_to_exam(
                grade=serializer.validated_data['grade'],
                academic_rank=serializer.validated_data['academic_rank']
            )
            
            # Create session using SessionService
            session = SessionService.create_session(
                student_data={
                    'student_name': serializer.validated_data['student_name'],
                    'parent_phone': serializer.validated_data.get('parent_phone', ''),
                    'school_name': serializer.validated_data.get('school_name', ''),
                    'academic_rank': serializer.validated_data['academic_rank'],
                },
                grade=serializer.validated_data['grade'],
                exam=exam,
                curriculum_level=curriculum_level
            )
            
            # Store session ID in request session
            request.session['session_id'] = str(session.id)
            request.session['exam_id'] = str(exam.id)
            
            # Log session creation
            ActivityLogger.log_user_action(
                user_id=session.student_name,
                action='start_test',
                details={
                    'session_id': str(session.id),
                    'exam_id': str(exam.id),
                    'grade': session.grade
                }
            )
            
            response_serializer = StudentSessionDetailSerializer(
                session, 
                context={'request': request}
            )
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Submit a single answer."""
        session = self.get_object()
        
        if session.completed_at:
            return Response(
                {'error': 'Session already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = SessionService.save_answer(
                session_id=pk,
                question_id=serializer.validated_data['question_id'],
                answer=serializer.validated_data['answer']
            )
            
            if result:
                # Clear session cache
                CacheService.delete(f"session_status:{pk}", prefix='session')
                
                return Response({'success': True, 'message': 'Answer saved'})
            else:
                return Response(
                    {'error': 'Failed to save answer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Failed to save answer: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def submit_batch(self, request, pk=None):
        """Submit multiple answers at once."""
        session = self.get_object()
        
        if session.completed_at:
            return Response(
                {'error': 'Session already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = BatchAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                saved_count = 0
                for answer_data in serializer.validated_data['answers']:
                    result = SessionService.save_answer(
                        session_id=pk,
                        question_id=answer_data['question_id'],
                        answer=answer_data['answer']
                    )
                    if result:
                        saved_count += 1
                
                # Clear session cache
                CacheService.delete(f"session_status:{pk}", prefix='session')
                
                return Response({
                    'success': True,
                    'saved_count': saved_count,
                    'total': len(serializer.validated_data['answers'])
                })
                
        except Exception as e:
            logger.error(f"Failed to save batch answers: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a test session and calculate results."""
        session = self.get_object()
        
        if session.completed_at:
            return Response(
                {'error': 'Session already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Grade the session
            results = GradingService.grade_session(str(session.id))
            
            # Mark as complete
            session.completed_at = timezone.now()
            session.save()
            
            # Clear caches
            CacheService.clear_session_cache(str(session.id))
            CacheService.clear_dashboard_cache()
            
            # Log completion
            ActivityLogger.log_user_action(
                user_id=session.student_name,
                action='complete_test',
                details={
                    'session_id': str(session.id),
                    'score': results['percentage'],
                    'correct': results['correct']
                }
            )
            
            # Prepare response
            result_serializer = TestResultSerializer(data={
                'session_id': session.id,
                'total_questions': results['total_questions'],
                'answered': results['answered'],
                'correct': results['correct'],
                'score': results['score'],
                'percentage': results['percentage'],
                'placement_level': str(session.final_curriculum_level) if session.final_curriculum_level else 'Not determined'
            })
            result_serializer.is_valid()
            
            return Response(result_serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to complete session: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get current session status."""
        session = self.get_object()
        
        # Try to get from cache first
        cache_key = f"session_status:{pk}"
        cached_status = CacheService.get(cache_key, prefix='session')
        
        if cached_status:
            return Response(cached_status)
        
        # Calculate status
        answered_questions = session.answers.values_list(
            'question__question_number', 
            flat=True
        )
        
        time_elapsed = (timezone.now() - session.started_at).total_seconds()
        time_remaining = max(0, (session.exam.timer_minutes * 60) - time_elapsed)
        
        current_question = 1
        if answered_questions:
            current_question = max(answered_questions) + 1
        
        status_data = {
            'session_id': session.id,
            'status': 'completed' if session.completed_at else 'in_progress',
            'progress': len(answered_questions),
            'time_remaining': int(time_remaining),
            'answered_questions': list(answered_questions),
            'current_question': current_question
        }
        
        # Cache for 30 seconds
        CacheService.set(cache_key, status_data, prefix='session', timeout=30)
        
        serializer = SessionStatusSerializer(status_data)
        return Response(serializer.data)


class SchoolViewSet(viewsets.ModelViewSet):
    """ViewSet for School operations."""
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsTeacherOrReadOnly]


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Program hierarchy (read-only)."""
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    
    def get_queryset(self):
        """Optimize with prefetch_related."""
        return super().get_queryset().prefetch_related(
            'subprograms__levels'
        ).order_by('order')


# PlacementRuleViewSet commented out - PlacementRule model doesn't exist
# class PlacementRuleViewSet(viewsets.ModelViewSet):
#     """ViewSet for PlacementRule operations."""
#     queryset = PlacementRule.objects.all()
#     serializer_class = PlacementRuleSerializer
#     permission_classes = [IsTeacherOrReadOnly]
#     
#     def get_queryset(self):
#         """Optimize with select_related."""
#         return super().get_queryset().select_related(
#             'curriculum_level__subprogram__program'
#         ).order_by('grade', 'priority')


# Dashboard API Views

class DashboardAPIView(APIView):
    """Dashboard statistics API."""
    permission_classes = [permissions.IsAuthenticated]
    
    @cache_result(prefix='dashboard', timeout=300)
    def get(self, request):
        """Get dashboard statistics."""
        stats = DashboardService.get_dashboard_stats()
        recent_sessions = DashboardService.get_recent_sessions(limit=10)
        exam_stats = DashboardService.get_exam_statistics()
        
        data = {
            'total_sessions': stats['total_sessions'],
            'active_exams': stats['active_exams'],
            'completed_today': stats.get('completed_today', 0),
            'average_score': stats.get('average_score', 0),
            'recent_sessions': StudentSessionSerializer(
                recent_sessions, 
                many=True,
                context={'request': request}
            ).data,
            'exam_statistics': exam_stats
        }
        
        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)


# Health Check API

class HealthCheckAPIView(APIView):
    """System health check endpoint."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get system health status."""
        from core.monitoring_service import HealthCheckService
        
        health = HealthCheckService.get_system_health()
        
        status_code = status.HTTP_200_OK
        if health['status'] == 'unhealthy':
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif health['status'] == 'degraded':
            status_code = status.HTTP_207_MULTI_STATUS
        
        return Response(health, status=status_code)