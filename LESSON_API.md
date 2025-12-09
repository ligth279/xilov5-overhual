# Lesson System API Documentation

## Overview
RESTful API endpoints for the Xilo AI Tutor lesson system, following AI Playground backend service architecture patterns.

**Base URL:** `http://localhost:5000`

**Response Format:** All endpoints return JSON with the following structure:
```json
{
  "code": 0,           // 0 = success, -1 = error
  "message": "string", // Success or error message
  "data": {}           // Response data (varies by endpoint)
}
```

---

## Endpoints

### 1. Get All Grades
Get list of all available grades.

**Endpoint:** `GET /api/lessons/grades`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "grades": [
      {
        "id": "grade_5",
        "name": "Grade 5",
        "subjects": ["math", "english", "science"]
      }
    ]
  }
}
```

---

### 2. Get Subjects for Grade
Get all subjects available for a specific grade.

**Endpoint:** `GET /api/lessons/<grade>/subjects`

**Parameters:**
- `grade` (path): Grade ID (e.g., `grade_5`)

**Example:** `GET /api/lessons/grade_5/subjects`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "grade": "grade_5",
    "subjects": [
      {
        "id": "math",
        "name": "Mathematics",
        "lesson_count": 1
      },
      {
        "id": "english",
        "name": "English",
        "lesson_count": 1
      }
    ]
  }
}
```

---

### 3. Get Lessons for Subject
Get all lessons for a specific grade and subject.

**Endpoint:** `GET /api/lessons/<grade>/<subject>`

**Parameters:**
- `grade` (path): Grade ID
- `subject` (path): Subject ID

**Example:** `GET /api/lessons/grade_5/math`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "grade": "grade_5",
    "subject": "math",
    "lessons": [
      {
        "id": "fractions_basic",
        "title": "Introduction to Fractions",
        "file": "lessons/grade_5/math/fractions_basic.json",
        "difficulty": "beginner",
        "estimated_time_minutes": 30,
        "prerequisites": []
      }
    ]
  }
}
```

---

### 4. Get Full Lesson
Get complete lesson data including all sections and questions.

**Endpoint:** `GET /api/lessons/<grade>/<subject>/<lesson_id>`

**Parameters:**
- `grade` (path): Grade ID
- `subject` (path): Subject ID
- `lesson_id` (path): Lesson ID

**Example:** `GET /api/lessons/grade_5/math/fractions_basic`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "lesson": {
      "id": "fractions_basic",
      "title": "Introduction to Fractions",
      "grade": "grade_5",
      "subject": "math",
      "difficulty": "beginner",
      "estimated_time_minutes": 30,
      "prerequisites": [],
      "learning_objectives": ["obj1", "obj2"],
      "sections": [
        {
          "id": "section_1",
          "title": "What are Fractions?",
          "type": "explanation",
          "content": "Educational content...",
          "allow_doubts": true,
          "doubt_prompt": "Ask me anything!",
          "ready_message": "Let's test your understanding!",
          "questions": [...]
        }
      ],
      "summary": "Lesson summary",
      "next_lessons": []
    }
  }
}
```

---

### 5. Get Section
Get a specific section from a lesson.

**Endpoint:** `GET /api/lessons/<grade>/<subject>/<lesson_id>/section/<section_id>`

**Parameters:**
- `grade` (path): Grade ID
- `subject` (path): Subject ID
- `lesson_id` (path): Lesson ID
- `section_id` (path): Section ID

**Example:** `GET /api/lessons/grade_5/math/fractions_basic/section/section_1`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "section": {
      "id": "section_1",
      "title": "What are Fractions?",
      "type": "explanation",
      "content": "A fraction represents...",
      "allow_doubts": true,
      "doubt_prompt": "Do you have any questions?",
      "ready_message": "Great! Now let's test your understanding.",
      "questions": [
        {
          "id": "q1",
          "question": "What do we call the top number?",
          "answer": "numerator",
          "evaluation_criteria": ["numerator"],
          "hints": ["It tells you how many parts you have"]
        }
      ]
    }
  }
}
```

---

### 6. Doubt Clearing Chat
Chat with AI during the doubt clearing phase of a section.

**Endpoint:** `POST /api/lessons/doubt-chat`

**Request Body:**
```json
{
  "message": "Can you give me another example?",
  "grade": "grade_5",
  "subject": "math",
  "lesson_id": "fractions_basic",
  "section_id": "section_1",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "response": "Sure! Let me give you another example of fractions...",
    "metadata": {
      "generation_time": 2.34,
      "section_id": "section_1"
    }
  }
}
```

**Notes:**
- Context-aware: AI knows the current section topic
- Maintains conversation history per section
- Uses Phi-3.5 for generating explanations
- Temperature: 0.7 (more creative for explanations)

---

### 7. Evaluate Answer
Evaluate a student's answer to a question.

**Endpoint:** `POST /api/lessons/evaluate-answer`

**Request Body:**
```json
{
  "grade": "grade_5",
  "subject": "math",
  "lesson_id": "fractions_basic",
  "section_id": "section_1",
  "question_id": "q1",
  "answer": "numerator",
  "use_ai": false
}
```

**Parameters:**
- `grade` (required): Grade ID
- `subject` (required): Subject ID
- `lesson_id` (required): Lesson ID
- `section_id` (required): Section ID
- `question_id` (required): Question ID
- `answer` (required): Student's answer
- `use_ai` (optional): Use AI evaluation (default: false)

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "evaluation": {
      "is_correct": true,
      "confidence": 1.0,
      "feedback": "Excellent! That's correct! 🎉",
      "expected_answer": null
    },
    "metadata": {
      "evaluation_time": 0.01,
      "method": "simple"
    }
  }
}
```

**Evaluation Methods:**
1. **Simple (use_ai: false)** - Fast keyword matching
   - Checks exact matches and contains logic
   - Returns confidence: 1.0 (exact), 0.9 (contains), 0.0 (wrong)
   
2. **AI (use_ai: true)** - Intelligent evaluation with Phi-3.5
   - Understands synonyms and variations
   - Provides detailed feedback
   - Slower but more accurate

---

### 8. Get Hint
Get a hint for a question.

**Endpoint:** `POST /api/lessons/get-hint`

**Request Body:**
```json
{
  "grade": "grade_5",
  "subject": "math",
  "lesson_id": "fractions_basic",
  "section_id": "section_1",
  "question_id": "q1",
  "hint_level": 0
}
```

**Parameters:**
- `grade` (required): Grade ID
- `subject` (required): Subject ID
- `lesson_id` (required): Lesson ID
- `section_id` (required): Section ID
- `question_id` (required): Question ID
- `hint_level` (required): Hint level (0 = first hint, 1 = second hint, etc.)

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "hint": "It tells you how many parts you have",
    "hint_level": 0
  }
}
```

---

### 9. Search Lessons
Search for lessons by keyword.

**Endpoint:** `GET /api/lessons/search?q=<query>`

**Parameters:**
- `q` (query): Search query

**Example:** `GET /api/lessons/search?q=fraction`

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "query": "fraction",
    "results": [
      {
        "id": "fractions_basic",
        "title": "Introduction to Fractions",
        "grade": "grade_5",
        "grade_name": "Grade 5",
        "subject": "math",
        "subject_name": "Mathematics",
        "difficulty": "beginner",
        "estimated_time_minutes": 30,
        "prerequisites": []
      }
    ],
    "count": 1
  }
}
```

---

### 10. Clear Lesson Session
Clear chat history for a specific lesson section.

**Endpoint:** `POST /api/lessons/clear-session`

**Request Body:**
```json
{
  "session_id": "optional_session_id",
  "lesson_id": "fractions_basic",
  "section_id": "section_1"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "Lesson session cleared successfully"
}
```

---

## Complete Lesson Flow API Usage

### Phase 1: Load Lesson
```javascript
// Get lesson
const lesson = await fetch('/api/lessons/grade_5/math/fractions_basic')
  .then(r => r.json());

// Get first section
const section = lesson.data.lesson.sections[0];
```

### Phase 2: Show Content
```javascript
// Display section.content to student
displayContent(section.content);
```

### Phase 3: Doubt Clearing
```javascript
// Student asks questions
const response = await fetch('/api/lessons/doubt-chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: "Can you explain more?",
    grade: "grade_5",
    subject: "math",
    lesson_id: "fractions_basic",
    section_id: "section_1"
  })
}).then(r => r.json());

// Display AI response
displayMessage(response.data.response);
```

### Phase 4: Student Ready
```javascript
// Student clicks "I'm Ready to Move On"
showQuestions(section.questions);
```

### Phase 5: Assessment
```javascript
// Student answers question
const evaluation = await fetch('/api/lessons/evaluate-answer', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    grade: "grade_5",
    subject: "math",
    lesson_id: "fractions_basic",
    section_id: "section_1",
    question_id: "q1",
    answer: studentAnswer,
    use_ai: false  // or true for better evaluation
  })
}).then(r => r.json());

if (evaluation.data.evaluation.is_correct) {
  showSuccess();
  nextQuestion();
} else {
  showFeedback(evaluation.data.evaluation.feedback);
}
```

### Get Hint (if needed)
```javascript
const hint = await fetch('/api/lessons/get-hint', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    grade: "grade_5",
    subject: "math",
    lesson_id: "fractions_basic",
    section_id: "section_1",
    question_id: "q1",
    hint_level: 0  // Increment for more hints
  })
}).then(r => r.json());

showHint(hint.data.hint);
```

---

## Error Handling

All endpoints return standard error responses:

```json
{
  "code": -1,
  "message": "Error description"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (missing parameters, invalid data)
- `404` - Resource not found (lesson, section, question)
- `500` - Internal server error
- `503` - Service unavailable (model not ready)

---

## Testing

Use the test script to verify all endpoints:

```bash
python test_lesson_api.py
```

Or test manually with curl:

```bash
# Get all grades
curl http://localhost:5000/api/lessons/grades

# Get lesson
curl http://localhost:5000/api/lessons/grade_5/math/fractions_basic

# Evaluate answer
curl -X POST http://localhost:5000/api/lessons/evaluate-answer \
  -H "Content-Type: application/json" \
  -d '{
    "grade": "grade_5",
    "subject": "math",
    "lesson_id": "fractions_basic",
    "section_id": "section_1",
    "question_id": "q1",
    "answer": "numerator",
    "use_ai": false
  }'
```

---

## Notes

- All chat features require the Phi-3.5 model to be loaded and ready
- Session IDs default to client IP address if not provided
- Conversation history is maintained per section during doubt clearing
- Answer evaluation can use simple (fast) or AI (accurate) methods
- Hints are progressive - request higher levels for more help

