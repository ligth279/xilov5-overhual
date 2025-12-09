# Progress Tracking API Documentation

## Overview
Track student learning progress including lesson completion, section progress, question answers, scores, and study time.

**Base URL:** `http://localhost:5000`

**Storage:** Progress is saved in JSON files under `user_progress/` directory (can be upgraded to database later).

---

## Progress Data Structure

Each user has a progress file: `user_progress/{user_id}.json`

```json
{
  "user_id": "student_123",
  "created_at": "2025-11-09T10:00:00",
  "last_active": "2025-11-09T15:30:00",
  "lessons": {
    "grade_5/math/fractions_basic": {
      "grade": "grade_5",
      "subject": "math",
      "lesson_id": "fractions_basic",
      "status": "completed",
      "started_at": "2025-11-09T10:00:00",
      "completed_at": "2025-11-09T11:30:00",
      "current_section": "section_3",
      "sections_completed": ["section_1", "section_2", "section_3"],
      "questions_answered": {
        "q1": {
          "correct": true,
          "attempts": 1,
          "hints_used": 0,
          "first_attempt_correct": true,
          "answered_at": "2025-11-09T10:15:00"
        }
      },
      "total_score": 85.7,
      "total_questions": 7,
      "time_spent_minutes": 30
    }
  },
  "stats": {
    "total_lessons_started": 3,
    "total_lessons_completed": 1,
    "total_sections_completed": 8,
    "total_questions_answered": 25,
    "total_questions_correct": 20,
    "total_time_minutes": 120
  }
}
```

---

## API Endpoints

### 1. Start Lesson
Mark a lesson as started. Creates initial progress record.

**Endpoint:** `POST /api/progress/start-lesson`

**Request Body:**
```json
{
  "user_id": "student_123",
  "grade": "grade_5",
  "subject": "math",
  "lesson_id": "fractions_basic"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "progress": {
      "grade": "grade_5",
      "subject": "math",
      "lesson_id": "fractions_basic",
      "status": "in_progress",
      "started_at": "2025-11-09T10:00:00",
      "sections_completed": [],
      "questions_answered": {}
    }
  }
}
```

---

### 2. Update Section Progress
Track section-level progress (in_progress or completed).

**Endpoint:** `POST /api/progress/update-section`

**Request Body:**
```json
{
  "user_id": "student_123",
  "grade": "grade_5",
  "subject": "math",
  "lesson_id": "fractions_basic",
  "section_id": "section_1",
  "status": "completed"
}
```

**Status Values:**
- `"in_progress"` - Section started
- `"completed"` - Section finished

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "progress": {
      "current_section": "section_1",
      "sections_completed": ["section_1"],
      ...
    }
  }
}
```

---

### 3. Record Answer
Track student's answer to a question.

**Endpoint:** `POST /api/progress/record-answer`

**Request Body:**
```json
{
  "user_id": "student_123",
  "grade": "grade_5",
  "subject": "math",
  "lesson_id": "fractions_basic",
  "question_id": "q1",
  "is_correct": true,
  "hints_used": 0
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "question_progress": {
      "correct": true,
      "attempts": 1,
      "hints_used": 0,
      "first_attempt_correct": true,
      "answered_at": "2025-11-09T10:15:00"
    }
  }
}
```

**Notes:**
- Can be called multiple times for the same question (tracks attempts)
- `first_attempt_correct` is true only if correct on first try with no hints
- Once `correct` is true, it stays true (student succeeded)

---

### 4. Complete Lesson
Mark a lesson as completed and calculate final score.

**Endpoint:** `POST /api/progress/complete-lesson`

**Request Body:**
```json
{
  "user_id": "student_123",
  "grade": "grade_5",
  "subject": "math",
  "lesson_id": "fractions_basic"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "progress": {
      "status": "completed",
      "completed_at": "2025-11-09T11:30:00",
      "total_questions": 7,
      "total_score": 85.7,
      ...
    }
  }
}
```

**Score Calculation:**
```
score = (correct_questions / total_questions) * 100
```

---

### 5. Get Lesson Progress
Retrieve progress for a specific lesson.

**Endpoint:** `GET /api/progress/lesson`

**Query Parameters:**
- `user_id` - User identifier
- `grade` - Grade ID
- `subject` - Subject ID
- `lesson_id` - Lesson ID

**Example:** `GET /api/progress/lesson?user_id=student_123&grade=grade_5&subject=math&lesson_id=fractions_basic`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "progress": {
      "grade": "grade_5",
      "subject": "math",
      "lesson_id": "fractions_basic",
      "status": "in_progress",
      "sections_completed": ["section_1"],
      "questions_answered": {...},
      "time_spent_minutes": 15
    }
  }
}
```

---

### 6. Get User Progress
Get complete progress for a user (all lessons).

**Endpoint:** `GET /api/progress/user`

**Query Parameters:**
- `user_id` - User identifier

**Example:** `GET /api/progress/user?user_id=student_123`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "progress": {
      "user_id": "student_123",
      "created_at": "2025-11-09T09:00:00",
      "last_active": "2025-11-09T15:30:00",
      "lessons": {...},
      "stats": {...}
    }
  }
}
```

---

### 7. Get Dashboard Stats
Get aggregated statistics for dashboard display.

**Endpoint:** `GET /api/progress/dashboard`

**Query Parameters:**
- `user_id` - User identifier

**Example:** `GET /api/progress/dashboard?user_id=student_123`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "stats": {
      "user_id": "student_123",
      "created_at": "2025-11-09T09:00:00",
      "last_active": "2025-11-09T15:30:00",
      "lessons_started": 3,
      "lessons_completed": 1,
      "completion_rate": 33.3,
      "sections_completed": 8,
      "questions_answered": 25,
      "questions_correct": 20,
      "accuracy": 80.0,
      "time_spent_minutes": 120
    }
  }
}
```

**Calculated Metrics:**
- `completion_rate` = (lessons_completed / lessons_started) * 100
- `accuracy` = (questions_correct / questions_answered) * 100

---

### 8. Get Subject Progress
Get progress for all lessons in a subject.

**Endpoint:** `GET /api/progress/subject`

**Query Parameters:**
- `user_id` - User identifier
- `grade` - Grade ID
- `subject` - Subject ID

**Example:** `GET /api/progress/subject?user_id=student_123&grade=grade_5&subject=math`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "progress": {
      "grade": "grade_5",
      "subject": "math",
      "lessons": {
        "fractions_basic": {...},
        "geometry_intro": {...}
      },
      "total_lessons": 2,
      "completed_lessons": 1
    }
  }
}
```

---

### 9. Add Study Time
Record time spent on a lesson.

**Endpoint:** `POST /api/progress/add-time`

**Request Body:**
```json
{
  "user_id": "student_123",
  "grade": "grade_5",
  "subject": "math",
  "lesson_id": "fractions_basic",
  "minutes": 15
}
```

**Response:**
```json
{
  "code": 0,
  "message": "Study time recorded"
}
```

**Notes:**
- Time is cumulative (adds to existing time)
- Updates both lesson time and global stats

---

### 10. Check Prerequisites
Check if user has completed prerequisite lessons.

**Endpoint:** `GET /api/progress/check-prerequisites`

**Query Parameters:**
- `user_id` - User identifier
- `prerequisites` - Comma-separated lesson IDs

**Example:** `GET /api/progress/check-prerequisites?user_id=student_123&prerequisites=fractions_basic,decimals_intro`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "can_access": true,
    "prerequisites": ["fractions_basic", "decimals_intro"]
  }
}
```

**Notes:**
- Returns `true` if ALL prerequisites are completed
- Returns `true` if no prerequisites (empty list)
- Use this before allowing access to a lesson

---

### 11. Reset Lesson
Reset progress for a specific lesson.

**Endpoint:** `POST /api/progress/reset-lesson`

**Request Body:**
```json
{
  "user_id": "student_123",
  "grade": "grade_5",
  "subject": "math",
  "lesson_id": "fractions_basic"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "Lesson reset successfully"
}
```

---

## Complete Workflow Example

### JavaScript Frontend Integration

```javascript
// 1. Start lesson
await fetch('/api/progress/start-lesson', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: userId,
    grade: 'grade_5',
    subject: 'math',
    lesson_id: 'fractions_basic'
  })
});

// 2. Track section progress
await fetch('/api/progress/update-section', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: userId,
    grade: 'grade_5',
    subject: 'math',
    lesson_id: 'fractions_basic',
    section_id: 'section_1',
    status: 'in_progress'
  })
});

// 3. Student answers question
const evaluation = await evaluateAnswer(question, answer);

// 4. Record the answer
await fetch('/api/progress/record-answer', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: userId,
    grade: 'grade_5',
    subject: 'math',
    lesson_id: 'fractions_basic',
    question_id: 'q1',
    is_correct: evaluation.is_correct,
    hints_used: hintsUsedCount
  })
});

// 5. Complete section
await fetch('/api/progress/update-section', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    ...
    status: 'completed'
  })
});

// 6. Complete lesson
await fetch('/api/progress/complete-lesson', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: userId,
    grade: 'grade_5',
    subject: 'math',
    lesson_id: 'fractions_basic'
  })
});

// 7. Show dashboard
const stats = await fetch(`/api/progress/dashboard?user_id=${userId}`)
  .then(r => r.json());
displayDashboard(stats.data.stats);
```

---

## Testing

Run the test script:
```bash
python test_progress_api.py
```

This will simulate a complete lesson flow and show all progress tracking features.

---

## Data Persistence

**Storage Location:** `user_progress/{user_id}.json`

**Benefits:**
- ✅ Simple file-based storage (no database needed initially)
- ✅ Human-readable JSON format
- ✅ Easy backup and migration
- ✅ Can upgrade to database later without API changes

**Future Upgrades:**
- Add PostgreSQL/SQLite database backend
- Add progress analytics and reports
- Add achievements and badges
- Add learning streaks and reminders

