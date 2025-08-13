# PrimePath API Documentation

## Overview

The PrimePath API provides programmatic access to placement test functionality, exam management, and curriculum configuration. All API endpoints are RESTful and return JSON responses.

## Base URL

```
Development: http://127.0.0.1:8000/api/
Production: https://yourdomain.com/api/
```

## Authentication

Most API endpoints require authentication. The API uses Django's session authentication for web clients and token authentication for programmatic access.

### Session Authentication
Web clients authenticate via the standard Django login:
```
POST /teacher/login/
```

### Token Authentication (Optional)
For programmatic access, obtain a token:
```
POST /api/auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Include the token in subsequent requests:
```
Authorization: Token your_token_here
```

## Response Format

All API responses follow this format:

### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict |
| 500 | Internal Server Error |

## Endpoints

### Exam Management

#### List Exams
```
GET /api/placement/exams/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "exams": [
      {
        "id": "uuid",
        "name": "CORE Phonics Level 1",
        "curriculum_level": "Level 1",
        "question_count": 30,
        "time_limit": 120,
        "created_at": "2025-08-13T10:00:00Z"
      }
    ],
    "count": 10,
    "next": null,
    "previous": null
  }
}
```

#### Get Exam Details
```
GET /api/placement/exams/{exam_id}/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "name": "CORE Phonics Level 1",
    "curriculum_level": "Level 1",
    "questions": [
      {
        "id": 1,
        "question_number": 1,
        "answer_key": "A",
        "points": 1,
        "audio_file": null
      }
    ],
    "audio_files": [],
    "pdf_file": "/media/exams/pdfs/exam.pdf",
    "time_limit": 120,
    "is_active": true
  }
}
```

#### Create Exam
```
POST /api/placement/exams/create/
Content-Type: multipart/form-data

{
  "name": "Exam Name",
  "curriculum_level_id": 1,
  "pdf_file": <file>,
  "audio_files": [<file>, <file>],
  "time_limit": 120,
  "questions": [
    {
      "question_number": 1,
      "answer_key": "A",
      "points": 1
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "exam_id": "uuid",
    "message": "Exam created successfully"
  }
}
```

#### Update Exam
```
PUT /api/placement/exams/{exam_id}/
Content-Type: application/json

{
  "name": "Updated Name",
  "time_limit": 90,
  "is_active": false
}
```

#### Delete Exam
```
DELETE /api/placement/exams/{exam_id}/
```

### Student Sessions

#### Start Test Session
```
POST /api/placement/start/
Content-Type: application/json

{
  "student_name": "John Doe",
  "grade": 10,
  "english_class_rank": 2,
  "phone_number": "+1234567890"  // optional
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid",
    "exam_id": "uuid",
    "test_url": "/placement/test/{session_id}/",
    "time_limit": 120
  }
}
```

#### Get Session Details
```
GET /api/placement/sessions/{session_id}/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "student_name": "John Doe",
    "exam": {
      "id": "uuid",
      "name": "CORE Phonics Level 1"
    },
    "started_at": "2025-08-13T10:00:00Z",
    "completed_at": null,
    "answers": [
      {
        "question_number": 1,
        "selected_answer": "B",
        "is_correct": false
      }
    ],
    "score": 0,
    "percentage": 0
  }
}
```

#### Submit Answer
```
POST /api/placement/sessions/{session_id}/submit-answer/
Content-Type: application/json

{
  "question_number": 1,
  "selected_answer": "B"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "saved": true,
    "question_number": 1,
    "selected_answer": "B"
  }
}
```

#### Complete Session
```
POST /api/placement/sessions/{session_id}/complete/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "score": 25,
    "total": 30,
    "percentage": 83.33,
    "recommended_level": "CORE Sigma Level 2",
    "result_url": "/placement/result/{session_id}/"
  }
}
```

#### List Sessions
```
GET /api/placement/sessions/
```

Query Parameters:
- `student_name`: Filter by student name
- `exam_id`: Filter by exam
- `completed`: Filter by completion status (true/false)
- `date_from`: Filter by start date (YYYY-MM-DD)
- `date_to`: Filter by end date (YYYY-MM-DD)

### Placement Rules

#### Get Placement Rules
```
GET /api/core/placement-rules/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "rules": [
      {
        "id": 1,
        "grade": 10,
        "english_class_rank": 1,
        "curriculum_level": {
          "id": 1,
          "name": "CORE Phonics Level 1"
        }
      }
    ]
  }
}
```

#### Create Placement Rule
```
POST /api/core/placement-rules/
Content-Type: application/json

{
  "grade": 10,
  "english_class_rank": 1,
  "curriculum_level_id": 1
}
```

#### Update Placement Rule
```
PUT /api/core/placement-rules/{rule_id}/
Content-Type: application/json

{
  "curriculum_level_id": 2
}
```

#### Delete Placement Rule
```
DELETE /api/core/placement-rules/{rule_id}/
```

### Curriculum Levels

#### List Curriculum Levels
```
GET /api/core/curriculum-levels/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "levels": [
      {
        "id": 1,
        "name": "CORE Phonics Level 1",
        "program": "CORE",
        "subprogram": "Phonics",
        "level_number": 1
      }
    ],
    "count": 44
  }
}
```

#### Get Curriculum Level
```
GET /api/core/curriculum-levels/{level_id}/
```

### Exam Mapping

#### Get Exam Mappings
```
GET /api/core/exam-mapping/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "mappings": [
      {
        "id": 1,
        "exam": {
          "id": "uuid",
          "name": "Placement Test 1"
        },
        "curriculum_level": {
          "id": 1,
          "name": "CORE Phonics Level 1"
        }
      }
    ]
  }
}
```

#### Create Exam Mapping
```
POST /api/core/exam-mapping/
Content-Type: application/json

{
  "exam_id": "uuid",
  "curriculum_level_id": 1
}
```

### Reports & Analytics

#### Get Session Statistics
```
GET /api/reports/session-stats/
```

Query Parameters:
- `period`: day, week, month, year
- `from_date`: Start date (YYYY-MM-DD)
- `to_date`: End date (YYYY-MM-DD)

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_sessions": 150,
    "completed_sessions": 120,
    "average_score": 75.5,
    "average_completion_time": 95,
    "by_level": [
      {
        "level": "CORE Phonics Level 1",
        "count": 45,
        "average_score": 72.3
      }
    ]
  }
}
```

#### Export Session Results
```
GET /api/reports/export/
```

Query Parameters:
- `format`: csv, excel, pdf
- `from_date`: Start date
- `to_date`: End date

### Audio Files

#### Upload Audio File
```
POST /api/placement/audio/upload/
Content-Type: multipart/form-data

{
  "exam_id": "uuid",
  "audio_file": <file>,
  "start_question": 1,
  "end_question": 5
}
```

#### Delete Audio File
```
DELETE /api/placement/audio/{audio_id}/
```

## Pagination

List endpoints support pagination:

```
GET /api/placement/exams/?page=2&page_size=20
```

Default page size: 10
Maximum page size: 100

## Filtering

Most list endpoints support filtering:

```
GET /api/placement/sessions/?completed=true&exam_id=uuid
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Bulk operations: 50 requests/hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1628856000
```

## Webhooks (Optional)

Configure webhooks to receive notifications:

```
POST /api/webhooks/
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["session.completed", "exam.created"],
  "secret": "your_webhook_secret"
}
```

### Webhook Events

- `session.started` - Test session started
- `session.completed` - Test session completed
- `session.timeout` - Session timed out
- `exam.created` - New exam created
- `exam.updated` - Exam updated
- `exam.deleted` - Exam deleted

## Error Codes

| Code | Description |
|------|-------------|
| AUTH_REQUIRED | Authentication required |
| INVALID_CREDENTIALS | Invalid username or password |
| PERMISSION_DENIED | User lacks required permissions |
| RESOURCE_NOT_FOUND | Requested resource not found |
| VALIDATION_ERROR | Input validation failed |
| DUPLICATE_RESOURCE | Resource already exists |
| RATE_LIMIT_EXCEEDED | Too many requests |
| SERVER_ERROR | Internal server error |

## Code Examples

### Python
```python
import requests

# Start a test session
url = "http://127.0.0.1:8000/api/placement/start/"
data = {
    "student_name": "John Doe",
    "grade": 10,
    "english_class_rank": 2
}

response = requests.post(url, json=data)
session_data = response.json()
session_id = session_data["data"]["session_id"]

# Submit an answer
answer_url = f"http://127.0.0.1:8000/api/placement/sessions/{session_id}/submit-answer/"
answer_data = {
    "question_number": 1,
    "selected_answer": "B"
}

response = requests.post(answer_url, json=answer_data)
```

### JavaScript
```javascript
// Start a test session
const startTest = async () => {
  const response = await fetch('/api/placement/start/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      student_name: 'John Doe',
      grade: 10,
      english_class_rank: 2
    })
  });
  
  const data = await response.json();
  return data.data.session_id;
};

// Submit an answer
const submitAnswer = async (sessionId, questionNumber, answer) => {
  const response = await fetch(`/api/placement/sessions/${sessionId}/submit-answer/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question_number: questionNumber,
      selected_answer: answer
    })
  });
  
  return await response.json();
};
```

### cURL
```bash
# Start a test session
curl -X POST http://127.0.0.1:8000/api/placement/start/ \
  -H "Content-Type: application/json" \
  -d '{"student_name":"John Doe","grade":10,"english_class_rank":2}'

# Submit an answer
curl -X POST http://127.0.0.1:8000/api/placement/sessions/{session_id}/submit-answer/ \
  -H "Content-Type: application/json" \
  -d '{"question_number":1,"selected_answer":"B"}'
```

## Testing

Use the API test endpoint to verify connectivity:

```
GET /api/health/
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-13T10:00:00Z",
  "version": "1.0.0"
}
```

## Support

For API support, please:
1. Check this documentation
2. Review error messages and codes
3. Contact technical support
4. Submit issues on GitHub

---

**API Version**: 1.0.0 | **Last Updated**: August 13, 2025