# Day 3: Student Management Architecture

## System Design

### Data Models

```python
# Student Enrollment Model
class StudentEnrollment(models.Model):
    """
    Represents a student's enrollment in a class.
    Many-to-many relationship with additional fields.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('transferred', 'Transferred'),
        ('graduated', 'Graduated')
    ], default='active')
    academic_year = models.CharField(max_length=9)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'class_assigned', 'academic_year']
        indexes = [
            models.Index(fields=['class_assigned', 'status']),
            models.Index(fields=['student', 'academic_year']),
        ]

# Update Student Model
class Student(models.Model):
    # Add these fields to existing model
    enrolled_classes = models.ManyToManyField(
        'Class',
        through='StudentEnrollment',
        related_name='enrolled_students'
    )
    current_grade_level = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
```

### API Endpoints

| Method | Endpoint | Purpose | Access |
|--------|----------|---------|--------|
| GET | /teacher/students/ | List students in teacher's classes | Teacher |
| POST | /teacher/students/enroll/ | Enroll student in class | Teacher |
| PUT | /teacher/students/{id}/update/ | Update student info | Teacher |
| DELETE | /teacher/students/{id}/unenroll/ | Remove from class | Teacher |
| GET | /teacher/students/search/ | Search students | Teacher |
| POST | /teacher/students/bulk-enroll/ | Bulk enrollment | Teacher |
| GET | /teacher/students/export/ | Export student list | Teacher |

### User Workflows

1. **Teacher Student Management Flow**
   ```
   Teacher Login → Dashboard → My Classes → Select Class → Manage Students
   → Add/Remove/Edit Students → Save Changes → Confirmation
   ```

2. **Bulk Enrollment Flow**
   ```
   Teacher → Import CSV → Validate Data → Preview Changes → Confirm Import
   → Show Results → Error Handling for Failed Entries
   ```

3. **Student Search Flow**
   ```
   Teacher → Search Box → Auto-complete → Filter by Class/Grade/Status
   → View Student Details → Edit/Transfer/Remove Actions
   ```

### Database Schema Changes

```sql
-- Add indexes for performance
CREATE INDEX idx_enrollment_class_status 
ON student_enrollment(class_assigned_id, status);

CREATE INDEX idx_enrollment_student_year 
ON student_enrollment(student_id, academic_year);

-- Add audit trigger
CREATE TRIGGER enrollment_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON student_enrollment
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

### Security Considerations

1. **Authorization Rules**
   - Teachers can only manage students in their assigned classes
   - Students can only view their own information
   - Admin has full access to all student data

2. **Data Protection**
   - PII fields encrypted at rest
   - Audit log for all student data changes
   - Soft delete for student records

3. **Input Validation**
   - Email format validation
   - Phone number format validation
   - Age/DOB reasonable range checks
   - Duplicate enrollment prevention

### Performance Optimization

1. **Query Optimization**
   - Use select_related for foreign keys
   - Prefetch_related for many-to-many
   - Pagination for large student lists
   - Caching for frequently accessed data

2. **Bulk Operations**
   - Batch inserts for CSV imports
   - Bulk update for status changes
   - Async processing for large exports

### Error Handling

1. **User-Friendly Messages**
   - "Student already enrolled in this class"
   - "Cannot remove student with pending assessments"
   - "Invalid date of birth (must be between 5-18 years old)"

2. **Rollback Scenarios**
   - Failed bulk enrollment rolls back entire batch
   - Maintains data consistency on errors
   - Detailed error logs for debugging