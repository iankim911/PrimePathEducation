"""
Custom exceptions for the PrimePath application.
These provide specific error handling for different scenarios.
"""

class PrimePathException(Exception):
    """Base exception for all PrimePath custom exceptions"""
    default_message = "An error occurred in PrimePath"
    
    def __init__(self, message=None, code=None, details=None):
        self.message = message or self.default_message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(PrimePathException):
    """Raised when data validation fails"""
    default_message = "Validation failed"


class PlacementRuleException(PrimePathException):
    """Raised when placement rule matching fails"""
    default_message = "No matching placement rule found"


class ExamNotFoundException(PrimePathException):
    """Raised when an exam cannot be found"""
    default_message = "Exam not found"


class ExamConfigurationException(PrimePathException):
    """Raised when exam configuration is invalid"""
    default_message = "Invalid exam configuration"


class SessionException(PrimePathException):
    """Base exception for session-related errors"""
    default_message = "Session error occurred"


class SessionAlreadyCompletedException(SessionException):
    """Raised when trying to modify a completed session"""
    default_message = "Session has already been completed"


class SessionNotFoundException(SessionException):
    """Raised when a session cannot be found"""
    default_message = "Session not found"


class FileProcessingException(PrimePathException):
    """Raised when file processing fails"""
    default_message = "File processing failed"


class AudioFileException(FileProcessingException):
    """Raised for audio file specific errors"""
    default_message = "Audio file processing failed"


class PDFFileException(FileProcessingException):
    """Raised for PDF file specific errors"""
    default_message = "PDF file processing failed"


class QuestionException(PrimePathException):
    """Raised for question-related errors"""
    default_message = "Question operation failed"


class AnswerValidationException(PrimePathException):
    """Raised when answer validation fails"""
    default_message = "Answer validation failed"


class PermissionException(PrimePathException):
    """Raised when user lacks required permissions"""
    default_message = "Permission denied"


class DatabaseException(PrimePathException):
    """Raised for database-related errors"""
    default_message = "Database operation failed"