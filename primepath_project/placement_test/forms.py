from django import forms
from .models import Exam, AudioFile, Question
from core.models import CurriculumLevel
from core.validators import validate_pdf_file, validate_audio_file


class ExamForm(forms.ModelForm):
    pdf_file = forms.FileField(
        validators=[validate_pdf_file],
        widget=forms.FileInput(attrs={'accept': '.pdf'})
    )
    
    class Meta:
        model = Exam
        fields = ['name', 'curriculum_level', 'pdf_file', 'timer_minutes', 
                 'total_questions', 'passing_score', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'curriculum_level': forms.Select(attrs={'class': 'form-control'}),
            'timer_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total_questions': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AudioFileForm(forms.ModelForm):
    audio_file = forms.FileField(
        validators=[validate_audio_file],
        widget=forms.FileInput(attrs={'accept': '.mp3,.wav,.m4a'})
    )
    
    class Meta:
        model = AudioFile
        fields = ['audio_file', 'start_question', 'end_question', 'order']
        widgets = {
            'start_question': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'end_question': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_number', 'question_type', 'correct_answer', 'points']
        widgets = {
            'question_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'correct_answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class StudentStartForm(forms.Form):
    student_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'})
    )
    school_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your school'})
    )
    grade = forms.IntegerField(
        min_value=1,
        max_value=12,
        widget=forms.Select(
            choices=[(i, f'Grade {i}') for i in range(1, 13)],
            attrs={'class': 'form-control'}
        )
    )
    academic_rank = forms.ChoiceField(
        choices=[
            ('TOP_10', 'Top 10%'),
            ('TOP_20', 'Top 20%'),
            ('TOP_30', 'Top 30%'),
            ('TOP_40', 'Top 40%'),
            ('TOP_50', 'Top 50%'),
            ('BELOW_50', 'Below 50%'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )