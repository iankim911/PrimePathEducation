"""
User Profile and Registration Models
Comprehensive user registration with social login support
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

# Phone number validator
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

# Korean phone validator
korean_phone_regex = RegexValidator(
    regex=r'^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$',
    message="Korean phone format: 010-XXXX-XXXX"
)

class UserProfile(models.Model):
    """Extended user profile for comprehensive registration"""
    
    # Link to Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Account Type
    ACCOUNT_TYPES = [
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
        ('PARENT', 'Parent'),
        ('ADMIN', 'Administrator'),
    ]
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='STUDENT')
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Contact Information
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    alternate_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Address
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='South Korea')
    
    # Educational Information
    school_name = models.CharField(max_length=255, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    student_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    
    BOARD_CHOICES = [
        ('CBSE', 'CBSE'),
        ('ICSE', 'ICSE'),
        ('IB', 'International Baccalaureate'),
        ('STATE', 'State Board'),
        ('KOREAN', 'Korean National Curriculum'),
        ('OTHER', 'Other'),
    ]
    board_curriculum = models.CharField(max_length=10, choices=BOARD_CHOICES, blank=True)
    
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('KO', 'Korean'),
        ('HI', 'Hindi'),
        ('ZH', 'Chinese'),
        ('JA', 'Japanese'),
        ('ES', 'Spanish'),
        ('OTHER', 'Other'),
    ]
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='EN')
    medium_of_instruction = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='EN')
    
    # Parent/Guardian Information (for students)
    parent_name = models.CharField(max_length=200, blank=True)
    parent_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    parent_email = models.EmailField(blank=True)
    parent_occupation = models.CharField(max_length=100, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    # Social Login Information
    AUTH_PROVIDERS = [
        ('EMAIL', 'Email'),
        ('GOOGLE', 'Google'),
        ('KAKAO', 'Kakao'),
    ]
    auth_provider = models.CharField(max_length=10, choices=AUTH_PROVIDERS, default='EMAIL')
    social_id = models.CharField(max_length=255, blank=True, db_index=True)
    social_profile_url = models.URLField(blank=True)
    profile_photo_url = models.URLField(blank=True)
    
    # Profile Completion
    profile_completion_percentage = models.IntegerField(default=0)
    profile_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    blood_group = models.CharField(max_length=5, blank=True)
    special_needs = models.TextField(blank=True, help_text="Any special accommodations required")
    previous_school = models.CharField(max_length=255, blank=True)
    siblings_in_system = models.ManyToManyField('self', blank=True, symmetrical=True)
    
    # Preferences
    STUDY_TIME_CHOICES = [
        ('MORNING', 'Morning (6AM-12PM)'),
        ('AFTERNOON', 'Afternoon (12PM-6PM)'),
        ('EVENING', 'Evening (6PM-10PM)'),
        ('NIGHT', 'Night (10PM-12AM)'),
    ]
    preferred_study_time = models.CharField(max_length=10, choices=STUDY_TIME_CHOICES, blank=True)
    timezone = models.CharField(max_length=50, default='Asia/Seoul')
    
    # Marketing & Analytics
    referral_source = models.CharField(max_length=100, blank=True)
    marketing_consent = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    privacy_policy_accepted = models.BooleanField(default=False)
    
    # System Fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_device = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'user_profiles'
        indexes = [
            models.Index(fields=['account_type', 'is_active']),
            models.Index(fields=['school_name', 'grade_level']),
            models.Index(fields=['auth_provider', 'social_id']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user.username})"
    
    def get_full_name(self):
        """Get user's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def calculate_age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            age = today.year - self.date_of_birth.year
            if today.month < self.date_of_birth.month or \
               (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
                age -= 1
            return age
        return None
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        required_fields = [
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'phone_number', 'address_line_1', 'city', 'country',
            'school_name', 'grade_level'
        ]
        
        if self.account_type == 'STUDENT':
            required_fields.extend(['parent_name', 'parent_phone', 'emergency_contact_name'])
        
        completed = 0
        for field in required_fields:
            if getattr(self, field):
                completed += 1
        
        percentage = int((completed / len(required_fields)) * 100)
        self.profile_completion_percentage = percentage
        
        if percentage == 100 and not self.profile_completed_at:
            self.profile_completed_at = timezone.now()
        
        return percentage
    
    def save(self, *args, **kwargs):
        """Override save to update profile completion"""
        self.calculate_profile_completion()
        super().save(*args, **kwargs)


class SocialAuthToken(models.Model):
    """Store OAuth tokens for social login providers"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_tokens')
    provider = models.CharField(max_length=10, choices=UserProfile.AUTH_PROVIDERS)
    access_token = models.TextField()  # Should be encrypted in production
    refresh_token = models.TextField(blank=True)  # Should be encrypted in production
    token_expiry = models.DateTimeField(null=True, blank=True)
    scope = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'provider']
        db_table = 'social_auth_tokens'
    
    def is_expired(self):
        """Check if token is expired"""
        if self.token_expiry:
            return timezone.now() > self.token_expiry
        return False


class EmailVerification(models.Model):
    """Email verification tokens"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'email_verifications'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_verified']),
        ]
    
    def is_expired(self):
        """Check if verification link is expired (24 hours)"""
        expiry_time = self.created_at + timezone.timedelta(hours=24)
        return timezone.now() > expiry_time


class PhoneVerification(models.Model):
    """Phone OTP verification"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=17)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'phone_verifications'
        indexes = [
            models.Index(fields=['user', 'is_verified']),
            models.Index(fields=['phone_number', 'otp_code']),
        ]
    
    def is_expired(self):
        """Check if OTP is expired (10 minutes)"""
        expiry_time = self.created_at + timezone.timedelta(minutes=10)
        return timezone.now() > expiry_time
    
    def can_retry(self):
        """Check if user can retry OTP (max 3 attempts)"""
        return self.attempts < 3


class LoginHistory(models.Model):
    """Track user login history"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    login_method = models.CharField(max_length=10, choices=UserProfile.AUTH_PROVIDERS)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_successful = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'login_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ip_address']),
        ]