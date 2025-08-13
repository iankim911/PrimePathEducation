# API v1 Endpoints

## Base URL
```
https://your-domain.com/api/v1/
```

## Authentication
Most endpoints require authentication using session-based authentication or API tokens.

## Endpoints

### Exams

#### List Exams
```
GET /api/v1/exams/
```
Returns a paginated list of exams.

#### Get Exam Details
```
GET /api/v1/exams/{id}/
```
Returns detailed information about a specific exam.

#### Create Exam
```
POST /api/v1/exams/
```
Creates a new exam (requires teacher authentication).

#### Update Exam
```
PUT /api/v1/exams/{id}/
PATCH /api/v1/exams/{id}/
```
Updates an existing exam.

#### Delete Exam
```
DELETE /api/v1/exams/{id}/
```
Deletes an exam.

### Student Sessions

#### List Sessions
```
GET /api/v1/sessions/
```
Returns a list of student test sessions.

#### Get Session Details
```
GET /api/v1/sessions/{id}/
```
Returns details of a specific session.

#### Start Test Session
```
POST /api/v1/placement/start/
```
Starts a new test session for a student.

Request Body:
```json
{
    "student_name": "John Doe",
    "grade": 5,
    "academic_rank": "TOP_50",
    "school_name": "Example School",
    "parent_phone": "555-1234"
}
```

#### Submit Answer
```
POST /api/v1/placement/session/{session_id}/submit/
```
Submits an answer for a question.

Request Body:
```json
{
    "question_id": "uuid",
    "answer": "Option A"
}
```

#### Complete Test
```
POST /api/v1/placement/session/{session_id}/complete/
```
Completes a test session and calculates results.

### Schools

#### List Schools
```
GET /api/v1/schools/
```
Returns a list of schools.

#### Get School Details
```
GET /api/v1/schools/{id}/
```
Returns details of a specific school.

### Programs

#### List Programs
```
GET /api/v1/programs/
```
Returns curriculum programs with hierarchy.

### Dashboard

#### Get Dashboard Statistics
```
GET /api/v1/dashboard/
```
Returns dashboard statistics (requires authentication).

### Health Check

#### API Health Status
```
GET /api/v1/health/
```
Returns API health status and version information.

## Response Format

All API responses follow this general format:

### Success Response
```json
{
    "success": true,
    "data": {
        // Response data
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": {}
    }
}
```

## Pagination

List endpoints support pagination using query parameters:

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

Example:
```
GET /api/v1/exams/?page=2&page_size=50
```

## Filtering

Many list endpoints support filtering:

```
GET /api/v1/sessions/?grade=5&completed=true
GET /api/v1/exams/?curriculum_level=1
```

## Rate Limiting

API requests are rate limited to:
- 1000 requests per hour for authenticated users
- 100 requests per hour for anonymous users

## Error Codes

Common error codes:

- `VALIDATION_ERROR`: Invalid input data
- `NOT_FOUND`: Resource not found
- `PERMISSION_DENIED`: Insufficient permissions
- `AUTHENTICATION_REQUIRED`: Authentication needed
- `RATE_LIMIT_EXCEEDED`: Too many requests

---

*Part of Phase 11: Final Integration & Testing*