"""
User Registration Forms
Multi-step registration with social login support
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from core.models.user_profile import UserProfile
import re
from datetime import date

class BasicRegistrationForm(UserCreationForm):
    """Step 1: Basic account creation"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    account_type = forms.ChoiceField(
        choices=UserProfile.ACCOUNT_TYPES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='STUDENT'
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I accept the Terms and Conditions"
    )
    
    privacy_policy_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I accept the Privacy Policy"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise ValidationError("Username must be at least 4 characters long.")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores.")
        return username


class PersonalInfoForm(forms.ModelForm):
    """Step 2: Personal information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'middle_name', 'last_name',
            'gender', 'date_of_birth',
            'phone_number', 'alternate_phone'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Middle Name (Optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'max': date.today().isoformat()
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+82 10-XXXX-XXXX'
            }),
            'alternate_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alternate Phone (Optional)'
            }),
        }
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            age = (date.today() - dob).days // 365
            if age < 5:
                raise ValidationError("User must be at least 5 years old.")
            if age > 100:
                raise ValidationError("Please enter a valid date of birth.")
        return dob
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove all non-digit characters
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) < 10:
                raise ValidationError("Phone number must be at least 10 digits.")
        return phone


class AddressForm(forms.ModelForm):
    """Step 3: Address information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'address_line_1', 'address_line_2',
            'city', 'state_province', 
            'postal_code', 'country'
        ]
        widgets = {
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, Suite, etc. (Optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state_province': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal/ZIP Code'
            }),
            'country': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('South Korea', 'South Korea'),
                ('United States', 'United States'),
                ('India', 'India'),
                ('China', 'China'),
                ('Japan', 'Japan'),
                ('Other', 'Other'),
            ]),
        }


class EducationalInfoForm(forms.ModelForm):
    """Step 4: Educational information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'school_name', 'grade_level', 'student_id',
            'board_curriculum', 'preferred_language',
            'medium_of_instruction', 'previous_school'
        ]
        widgets = {
            'school_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Current School Name'
            }),
            'grade_level': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', '-- Select Grade --'),
                ('K', 'Kindergarten'),
                ('1', 'Grade 1'), ('2', 'Grade 2'), ('3', 'Grade 3'),
                ('4', 'Grade 4'), ('5', 'Grade 5'), ('6', 'Grade 6'),
                ('7', 'Grade 7'), ('8', 'Grade 8'), ('9', 'Grade 9'),
                ('10', 'Grade 10'), ('11', 'Grade 11'), ('12', 'Grade 12'),
                ('UG', 'Undergraduate'), ('PG', 'Postgraduate'),
            ]),
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Student ID (Optional)'
            }),
            'board_curriculum': forms.Select(attrs={'class': 'form-select'}),
            'preferred_language': forms.Select(attrs={'class': 'form-select'}),
            'medium_of_instruction': forms.Select(attrs={'class': 'form-select'}),
            'previous_school': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Previous School (Optional)'
            }),
        }


class ParentGuardianForm(forms.ModelForm):
    """Step 5: Parent/Guardian information (for students)"""
    
    class Meta:
        model = UserProfile
        fields = [
            'parent_name', 'parent_phone', 'parent_email',
            'parent_occupation', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relation'
        ]
        widgets = {
            'parent_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian Full Name'
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian Phone'
            }),
            'parent_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian Email'
            }),
            'parent_occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian Occupation'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Phone'
            }),
            'emergency_contact_relation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Relationship to Student'
            }),
        }
    
    def clean_parent_email(self):
        email = self.cleaned_data.get('parent_email')
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValidationError("Please enter a valid email address.")
        return email


class AdditionalInfoForm(forms.ModelForm):
    """Step 6: Additional optional information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'blood_group', 'special_needs',
            'preferred_study_time', 'timezone',
            'referral_source', 'marketing_consent'
        ]
        widgets = {
            'blood_group': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', '-- Select Blood Group --'),
                ('A+', 'A+'), ('A-', 'A-'),
                ('B+', 'B+'), ('B-', 'B-'),
                ('AB+', 'AB+'), ('AB-', 'AB-'),
                ('O+', 'O+'), ('O-', 'O-'),
            ]),
            'special_needs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special accommodations or needs (Optional)'
            }),
            'preferred_study_time': forms.Select(attrs={'class': 'form-select'}),
            'timezone': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('Asia/Seoul', 'Seoul (GMT+9)'),
                ('Asia/Tokyo', 'Tokyo (GMT+9)'),
                ('Asia/Shanghai', 'Beijing/Shanghai (GMT+8)'),
                ('Asia/Kolkata', 'India (GMT+5:30)'),
                ('America/New_York', 'Eastern Time (GMT-5)'),
                ('America/Los_Angeles', 'Pacific Time (GMT-8)'),
                ('Europe/London', 'London (GMT+0)'),
            ]),
            'referral_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'How did you hear about us? (Optional)'
            }),
            'marketing_consent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class SocialAuthCompleteProfileForm(forms.ModelForm):
    """Form for completing profile after social login"""
    
    class Meta:
        model = UserProfile
        fields = [
            'phone_number', 'date_of_birth', 'gender',
            'address_line_1', 'city', 'country',
            'school_name', 'grade_level',
            'parent_name', 'parent_phone',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'required': True
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
                'required': True
            }),
            'country': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }, choices=[
                ('South Korea', 'South Korea'),
                ('United States', 'United States'),
                ('India', 'India'),
                ('Other', 'Other'),
            ]),
            'school_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'School Name',
                'required': True
            }),
            'grade_level': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }, choices=[
                ('', '-- Select Grade --'),
                ('1', 'Grade 1'), ('2', 'Grade 2'), ('3', 'Grade 3'),
                ('4', 'Grade 4'), ('5', 'Grade 5'), ('6', 'Grade 6'),
                ('7', 'Grade 7'), ('8', 'Grade 8'), ('9', 'Grade 9'),
                ('10', 'Grade 10'), ('11', 'Grade 11'), ('12', 'Grade 12'),
            ]),
            'parent_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian Name'
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian Phone'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Name',
                'required': True
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Phone',
                'required': True
            }),
        }