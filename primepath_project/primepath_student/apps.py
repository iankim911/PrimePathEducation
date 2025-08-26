from django.apps import AppConfig


class PrimepathStudentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'primepath_student'
    
    def ready(self):
        """Import signal handlers when app is ready"""
        import primepath_student.signals
