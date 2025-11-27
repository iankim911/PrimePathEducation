from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_size(file, max_size_mb=10):
    """Validates that uploaded file doesn't exceed max size"""
    file_size = file.size
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        raise ValidationError(
            _(f'File size exceeds {max_size_mb}MB limit. Current size: {file_size / (1024 * 1024):.2f}MB'),
            code='file_too_large'
        )


def validate_pdf_file(file):
    """Validates that file is a valid PDF"""
    validate_file_size(file, max_size_mb=10)
    
    if not file.name.lower().endswith('.pdf'):
        raise ValidationError(
            _('Only PDF files are allowed.'),
            code='invalid_file_type'
        )


def validate_audio_file(file):
    """Validates that file is a valid audio file"""
    validate_file_size(file, max_size_mb=50)
    
    allowed_extensions = ['.mp3', '.wav', '.m4a']
    if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError(
            _('Only MP3, WAV, and M4A audio files are allowed.'),
            code='invalid_file_type'
        )