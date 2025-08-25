from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import StudentProfile
import re


class StudentRegistrationForm(UserCreationForm):
    """Comprehensive student registration form"""
    
    # Basic User Information
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    # Student Profile Information
    student_id = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a unique student ID'
        }),
        help_text="This will be your login ID"
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number")],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        })
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    gender = forms.ChoiceField(
        choices=[('', 'Select gender')] + StudentProfile.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    grade = forms.ChoiceField(
        choices=[('', 'Select grade')] + StudentProfile.GRADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Contact Information
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your home address'
        })
    )
    emergency_contact_phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number")],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Emergency contact phone'
        })
    )
    
    # School Information
    school_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name of your school'
        })
    )
    school_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'School address'
        })
    )
    
    # Parent/Guardian 1 Information
    parent1_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parent/Guardian 1 name'
        })
    )
    parent1_phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number")],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parent/Guardian 1 phone'
        })
    )
    parent1_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parent/Guardian 1 email'
        })
    )
    
    # Parent/Guardian 2 Information
    parent2_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parent/Guardian 2 name (optional)'
        })
    )
    parent2_phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number")],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parent/Guardian 2 phone (optional)'
        })
    )
    parent2_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parent/Guardian 2 email (optional)'
        })
    )
    
    # Recovery Information
    recovery_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Recovery email (can be parent email)'
        }),
        help_text="This email will be used for password recovery"
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set username field to use student_id - make it not required since we'll set it programmatically
        self.fields['username'].widget = forms.HiddenInput()
        self.fields['username'].required = False
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise ValidationError("This student ID is already taken. Please choose another.")
        if User.objects.filter(username=student_id).exists():
            raise ValidationError("This student ID is already taken. Please choose another.")
        return student_id
    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if StudentProfile.objects.filter(phone_number=phone).exists():
            raise ValidationError("This phone number is already registered.")
        return phone
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        student_id = self.cleaned_data.get("student_id")
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("The two password fields didn't match.", code='password_mismatch')
            
            # Check Django password validation but provide user-friendly messages
            try:
                # Create a temporary user instance for validation
                user = User(username=student_id or '')
                validate_password(password2, user=user)
            except ValidationError as e:
                # Convert technical Django errors to user-friendly messages
                friendly_errors = []
                for error in e.messages:
                    if "similar" in error.lower() or "too similar" in error.lower():
                        friendly_errors.append(
                            f"Password cannot be too similar to your Student ID '{student_id}'. "
                            "Try using a completely different word or phrase."
                        )
                    elif "common" in error.lower() or "too common" in error.lower():
                        friendly_errors.append(
                            "This password is too common. Please choose a more unique password."
                        )
                    elif "numeric" in error.lower() or "entirely numeric" in error.lower():
                        friendly_errors.append(
                            "Password cannot be entirely numeric. Please include letters."
                        )
                    elif "short" in error.lower() or "at least" in error.lower():
                        friendly_errors.append(
                            "Password must be at least 8 characters long."
                        )
                    else:
                        # Keep original message for any other errors
                        friendly_errors.append(error)
                        
                if friendly_errors:
                    raise ValidationError(friendly_errors, code='password_invalid')
        
        return password2
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Automatically set username to student_id
        student_id = cleaned_data.get('student_id')
        if student_id:
            cleaned_data['username'] = student_id
        
        # Ensure at least one parent contact if student is under 18
        grade = cleaned_data.get('grade')
        if grade and grade in ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:
            parent1_name = cleaned_data.get('parent1_name')
            parent1_phone = cleaned_data.get('parent1_phone')
            
            if not parent1_name or not parent1_phone:
                raise ValidationError("Parent/Guardian information is required for students under 18.")
        
        return cleaned_data
    
    def save(self, commit=True):
        # Set username to student_id BEFORE calling parent save
        student_id = self.cleaned_data['student_id']
        
        # Set the username field in the instance before parent save
        if hasattr(self, 'instance'):
            self.instance.username = student_id
        
        # Also set in cleaned_data for parent form
        self.cleaned_data['username'] = student_id
        
        user = super().save(commit=False)
        user.username = student_id
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Create student profile
            profile = StudentProfile.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                phone_number=self.cleaned_data['phone_number'],
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender=self.cleaned_data.get('gender'),
                grade=self.cleaned_data.get('grade'),
                address=self.cleaned_data.get('address', ''),
                emergency_contact_phone=self.cleaned_data.get('emergency_contact_phone', ''),
                school_name=self.cleaned_data.get('school_name', ''),
                school_address=self.cleaned_data.get('school_address', ''),
                parent1_name=self.cleaned_data.get('parent1_name', ''),
                parent1_phone=self.cleaned_data.get('parent1_phone', ''),
                parent1_email=self.cleaned_data.get('parent1_email', ''),
                parent2_name=self.cleaned_data.get('parent2_name', ''),
                parent2_phone=self.cleaned_data.get('parent2_phone', ''),
                parent2_email=self.cleaned_data.get('parent2_email', ''),
                recovery_email=self.cleaned_data.get('recovery_email', '')
            )
        
        return user


class StudentPasswordResetForm(PasswordResetForm):
    """Enhanced password reset supporting phone and email recovery"""
    
    contact_method = forms.ChoiceField(
        choices=[
            ('email', 'Email Address'),
            ('phone', 'Phone Number'),
            ('student_id', 'Student ID + Recovery Email'),
        ],
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    email_or_phone = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email, phone, or student ID'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        contact_method = cleaned_data.get('contact_method')
        contact_value = cleaned_data.get('email_or_phone')
        
        if not contact_value:
            raise ValidationError("Please enter your contact information.")
        
        # Find user based on contact method
        user = None
        
        if contact_method == 'email':
            try:
                user = User.objects.get(email=contact_value)
            except User.DoesNotExist:
                raise ValidationError("No account found with this email address.")
        
        elif contact_method == 'phone':
            try:
                profile = StudentProfile.objects.get(phone_number=contact_value)
                user = profile.user
            except StudentProfile.DoesNotExist:
                raise ValidationError("No account found with this phone number.")
        
        elif contact_method == 'student_id':
            try:
                profile = StudentProfile.objects.get(student_id=contact_value)
                user = profile.user
                # Use recovery email if available, otherwise primary email
                if profile.recovery_email:
                    cleaned_data['email'] = profile.recovery_email
                else:
                    cleaned_data['email'] = user.email
            except StudentProfile.DoesNotExist:
                raise ValidationError("No account found with this student ID.")
        
        if user:
            cleaned_data['users_cache'] = [user]
        
        return cleaned_data


class StudentLoginForm(forms.Form):
    """Student login form supporting ID or phone"""
    
    login_method = forms.ChoiceField(
        choices=[
            ('student_id', 'Student ID'),
            ('phone', 'Phone Number'),
        ],
        initial='student_id',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    identifier = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Student ID or Phone Number'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        login_method = cleaned_data.get('login_method')
        identifier = cleaned_data.get('identifier')
        
        if not identifier:
            raise ValidationError("Please enter your Student ID or Phone Number.")
        
        # Find user based on login method
        user = None
        
        if login_method == 'student_id':
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                raise ValidationError("Invalid Student ID or password.")
        
        elif login_method == 'phone':
            try:
                profile = StudentProfile.objects.get(phone_number=identifier)
                user = profile.user
            except StudentProfile.DoesNotExist:
                raise ValidationError("Invalid phone number or password.")
        
        cleaned_data['user'] = user
        return cleaned_data


class StudentProfileUpdateForm(forms.ModelForm):
    """Form for updating student profile information"""
    
    class Meta:
        model = StudentProfile
        exclude = ['user', 'student_id', 'kakao_id', 'email_verified', 'phone_verified', 'created_at', 'updated_at']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your home address'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
            'school_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of your school'
            }),
            'school_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'School address'
            }),
            'parent1_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian 1 name'
            }),
            'parent1_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian 1 phone'
            }),
            'parent1_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian 1 email'
            }),
            'parent2_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian 2 name (optional)'
            }),
            'parent2_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian 2 phone (optional)'
            }),
            'parent2_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Parent/Guardian 2 email (optional)'
            }),
            'recovery_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Recovery email (can be parent email)'
            }),
        }