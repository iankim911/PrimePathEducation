"""
File Service - Handles PDF and audio file operations
Part of Phase 5 modularization
"""
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.exceptions import ValidationError
import logging
import hashlib
from pathlib import Path

# PyPDF2 is optional - service works without it but with reduced functionality
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    logger = logging.getLogger(__name__)
    logger.warning("PyPDF2 not installed. PDF validation will be limited.")

logger = logging.getLogger(__name__)


class FileService:
    """Service for file operations including PDF and audio files."""
    
    # File size limits (in bytes)
    MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Allowed file extensions
    ALLOWED_PDF_EXTENSIONS = ['.pdf']
    ALLOWED_AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.ogg']
    
    @staticmethod
    def validate_pdf_file(file):
        """Validate a PDF file before saving."""
        # Handle None file
        if file is None:
            return False
            
        try:
            # Check file size
            if not hasattr(file, 'size') or file.size > FileService.MAX_PDF_SIZE:
                raise ValidationError(
                    f"PDF file too large. Maximum size is {FileService.MAX_PDF_SIZE / 1024 / 1024}MB"
                )
            
            # Check file extension
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in FileService.ALLOWED_PDF_EXTENSIONS:
                raise ValidationError(
                    f"Invalid file type. Allowed types: {', '.join(FileService.ALLOWED_PDF_EXTENSIONS)}"
                )
            
            # Try to read PDF to validate it's a real PDF
            if HAS_PYPDF2:
                try:
                    file.seek(0)
                    pdf_reader = PyPDF2.PdfReader(file)
                    page_count = len(pdf_reader.pages)
                    file.seek(0)  # Reset file pointer
                    
                    if page_count == 0:
                        raise ValidationError("PDF file has no pages")
                    
                    return {
                        'valid': True,
                        'page_count': page_count,
                        'file_size': file.size
                    }
                    
                except Exception as e:
                    raise ValidationError(f"Invalid PDF file: {str(e)}")
            else:
                # Basic validation without PyPDF2
                file.seek(0)
                header = file.read(5)
                file.seek(0)
                
                # Check for PDF header
                if header != b'%PDF-':
                    raise ValidationError("File does not appear to be a valid PDF")
                
                return {
                    'valid': True,
                    'page_count': None,  # Can't determine without PyPDF2
                    'file_size': file.size
                }
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating PDF file: {e}")
            raise ValidationError("Could not validate PDF file")
    
    @staticmethod
    def validate_audio_file(file):
        """Validate an audio file before saving."""
        try:
            # Check file size
            if file.size > FileService.MAX_AUDIO_SIZE:
                raise ValidationError(
                    f"Audio file too large. Maximum size is {FileService.MAX_AUDIO_SIZE / 1024 / 1024}MB"
                )
            
            # Check file extension
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in FileService.ALLOWED_AUDIO_EXTENSIONS:
                raise ValidationError(
                    f"Invalid file type. Allowed types: {', '.join(FileService.ALLOWED_AUDIO_EXTENSIONS)}"
                )
            
            return {
                'valid': True,
                'file_size': file.size,
                'file_type': ext
            }
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            raise ValidationError("Could not validate audio file")
    
    @staticmethod
    def save_exam_pdf(file, exam_id):
        """Save an exam PDF file with proper naming and organization."""
        try:
            # Validate the file
            validation = FileService.validate_pdf_file(file)
            
            # Generate unique filename
            file_hash = hashlib.md5(file.read()).hexdigest()[:8]
            file.seek(0)
            
            filename = f"exam_{exam_id}_{file_hash}.pdf"
            file_path = f"exams/pdfs/{filename}"
            
            # Save file
            saved_path = default_storage.save(file_path, ContentFile(file.read()))
            
            return {
                'path': saved_path,
                'filename': filename,
                'page_count': validation['page_count'],
                'file_size': validation['file_size']
            }
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error saving exam PDF: {e}")
            raise ValidationError("Could not save PDF file")
    
    @staticmethod
    def save_audio_file(file, exam_id, question_range):
        """Save an audio file for exam questions."""
        try:
            # Validate the file
            validation = FileService.validate_audio_file(file)
            
            # Generate unique filename
            file_hash = hashlib.md5(file.read()).hexdigest()[:8]
            file.seek(0)
            
            ext = os.path.splitext(file.name)[1].lower()
            filename = f"audio_{exam_id}_q{question_range}_{file_hash}{ext}"
            file_path = f"exams/audio/{filename}"
            
            # Save file
            saved_path = default_storage.save(file_path, ContentFile(file.read()))
            
            return {
                'path': saved_path,
                'filename': filename,
                'file_size': validation['file_size'],
                'file_type': validation['file_type']
            }
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            raise ValidationError("Could not save audio file")
    
    @staticmethod
    def delete_file(file_path):
        """Safely delete a file."""
        try:
            if file_path and default_storage.exists(file_path):
                default_storage.delete(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_url(file_path):
        """Get the URL for a file."""
        try:
            if file_path and default_storage.exists(file_path):
                return default_storage.url(file_path)
            return None
        except Exception as e:
            logger.error(f"Error getting file URL for {file_path}: {e}")
            return None
    
    @staticmethod
    def get_file_info(file_path):
        """Get information about a file."""
        try:
            if not file_path or not default_storage.exists(file_path):
                return None
            
            file_size = default_storage.size(file_path)
            modified_time = default_storage.get_modified_time(file_path)
            
            return {
                'path': file_path,
                'size': file_size,
                'modified': modified_time,
                'url': FileService.get_file_url(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    @staticmethod
    def cleanup_orphaned_files():
        """Clean up files that are no longer referenced in the database."""
        from placement_test.models import PlacementExam as Exam, AudioFile
        
        try:
            cleaned = 0
            
            # Get all PDF files in storage
            pdf_dir = 'exams/pdfs'
            if default_storage.exists(pdf_dir):
                _, pdf_files = default_storage.listdir(pdf_dir)
                
                # Get all PDF files referenced in database
                db_pdfs = set(Exam.objects.values_list('pdf_file', flat=True))
                
                # Delete orphaned PDFs
                for pdf_file in pdf_files:
                    file_path = f"{pdf_dir}/{pdf_file}"
                    if file_path not in db_pdfs:
                        if FileService.delete_file(file_path):
                            cleaned += 1
                            logger.info(f"Deleted orphaned PDF: {file_path}")
            
            # Get all audio files in storage
            audio_dir = 'exams/audio'
            if default_storage.exists(audio_dir):
                _, audio_files = default_storage.listdir(audio_dir)
                
                # Get all audio files referenced in database
                db_audios = set(AudioFile.objects.values_list('audio_file', flat=True))
                
                # Delete orphaned audio files
                for audio_file in audio_files:
                    file_path = f"{audio_dir}/{audio_file}"
                    if file_path not in db_audios:
                        if FileService.delete_file(file_path):
                            cleaned += 1
                            logger.info(f"Deleted orphaned audio: {file_path}")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning up orphaned files: {e}")
            return 0
    
    @staticmethod
    def get_storage_usage():
        """Get storage usage statistics."""
        try:
            stats = {
                'pdf_count': 0,
                'pdf_size': 0,
                'audio_count': 0,
                'audio_size': 0,
                'total_size': 0
            }
            
            # Count PDF files
            pdf_dir = 'exams/pdfs'
            if default_storage.exists(pdf_dir):
                _, pdf_files = default_storage.listdir(pdf_dir)
                stats['pdf_count'] = len(pdf_files)
                
                for pdf_file in pdf_files:
                    file_path = f"{pdf_dir}/{pdf_file}"
                    stats['pdf_size'] += default_storage.size(file_path)
            
            # Count audio files
            audio_dir = 'exams/audio'
            if default_storage.exists(audio_dir):
                _, audio_files = default_storage.listdir(audio_dir)
                stats['audio_count'] = len(audio_files)
                
                for audio_file in audio_files:
                    file_path = f"{audio_dir}/{audio_file}"
                    stats['audio_size'] += default_storage.size(file_path)
            
            stats['total_size'] = stats['pdf_size'] + stats['audio_size']
            
            # Convert to MB for readability
            stats['pdf_size_mb'] = stats['pdf_size'] / 1024 / 1024
            stats['audio_size_mb'] = stats['audio_size'] / 1024 / 1024
            stats['total_size_mb'] = stats['total_size'] / 1024 / 1024
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage usage: {e}")
            return {
                'pdf_count': 0,
                'pdf_size': 0,
                'audio_count': 0,
                'audio_size': 0,
                'total_size': 0
            }