from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from primepath_student.models import StudentProfile
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


@login_required
def student_profile(request):
    """View for displaying and editing student profile"""
    # Check if user has student profile
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "You don't have a student profile. Please contact support.")
        return redirect('primepath_student:login')
    
    # Handle POST request for profile updates
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # Update phone number
            phone_number = request.POST.get('phone_number', '').strip()
            if phone_number:
                student_profile.phone_number = phone_number
            
            # Update grade
            grade = request.POST.get('grade', '').strip()
            if grade:
                student_profile.grade = grade
            
            # Update recovery email
            recovery_email = request.POST.get('recovery_email', '').strip()
            if recovery_email:
                student_profile.recovery_email = recovery_email
                request.user.email = recovery_email  # Also update User email
                request.user.save()
            
            # Update parent information
            parent1_name = request.POST.get('parent1_name', '').strip()
            if parent1_name:
                student_profile.parent1_name = parent1_name
            
            parent1_phone = request.POST.get('parent1_phone', '').strip()
            if parent1_phone:
                student_profile.parent1_phone = parent1_phone
            
            parent2_name = request.POST.get('parent2_name', '').strip()
            if parent2_name:
                student_profile.parent2_name = parent2_name
            
            parent2_phone = request.POST.get('parent2_phone', '').strip()
            if parent2_phone:
                student_profile.parent2_phone = parent2_phone
            
            student_profile.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('primepath_student:profile')
        
        elif action == 'change_password':
            # Handle password change
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not request.user.check_password(old_password):
                messages.error(request, "Your old password was entered incorrectly.")
            elif new_password1 != new_password2:
                messages.error(request, "The two password fields didn't match.")
            elif len(new_password1) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
            else:
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keep user logged in
                messages.success(request, "Your password has been changed successfully!")
                return redirect('primepath_student:profile')
    
    # Get class assignments for display
    class_assignments = student_profile.class_assignments.filter(is_active=True)
    
    context = {
        'student': student_profile,
        'user': request.user,
        'class_assignments': class_assignments
    }
    
    return render(request, 'primepath_student/profile.html', context)