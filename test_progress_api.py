"""
Test Progress Tracking System
"""
import requests
import json

BASE_URL = "http://localhost:5000"
USER_ID = "test_student_123"

def test_api(endpoint, method="GET", data=None, params=None):
    """Helper to test API endpoints"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"{method} {endpoint}")
    print('='*60)
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.post(url, json=data)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)[:500]}...")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("Testing Progress Tracking System")
    print("="*60)
    
    # Test 1: Start a lesson
    print("\n📊 Test 1: Start Lesson")
    test_api("/api/progress/start-lesson", "POST", {
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic"
    })
    
    # Test 2: Update section progress
    print("\n📊 Test 2: Start Section 1")
    test_api("/api/progress/update-section", "POST", {
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "section_id": "section_1",
        "status": "in_progress"
    })
    
    # Test 3: Record correct answer
    print("\n📊 Test 3: Record Correct Answer (Question 1)")
    test_api("/api/progress/record-answer", "POST", {
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "question_id": "q1",
        "is_correct": True,
        "hints_used": 0
    })
    
    # Test 4: Record incorrect answer with hint
    print("\n📊 Test 4: Record Incorrect Answer (Question 2)")
    test_api("/api/progress/record-answer", "POST", {
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "question_id": "q2",
        "is_correct": False,
        "hints_used": 1
    })
    
    # Test 5: Record correct answer after hint
    print("\n📊 Test 5: Record Correct Answer After Hint (Question 2)")
    test_api("/api/progress/record-answer", "POST", {
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "question_id": "q2",
        "is_correct": True,
        "hints_used": 1
    })
    
    # Test 6: Complete section
    print("\n📊 Test 6: Complete Section 1")
    test_api("/api/progress/update-section", "POST", {
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "section_id": "section_1",
        "status": "completed"
    })
    
    # Test 7: Add more answers for other sections
    print("\n📊 Test 7: Answer Questions in Section 2")
    for i in range(3, 5):  # q3, q4
        test_api("/api/progress/record-answer", "POST", {
            "user_id": USER_ID,
            "grade": "grade_5",
            "subject": "math",
            "lesson_id": "fractions_basic",
            "question_id": f"q{i}",
            "is_correct": True,
            "hints_used": 0
        })
    
    # Test 8: Add study time
    print("\n📊 Test 8: Add Study Time (15 minutes)")
    test_api("/api/progress/add-time", "POST", {
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "minutes": 15
    })
    
    # Test 9: Get lesson progress
    print("\n📊 Test 9: Get Lesson Progress")
    test_api("/api/progress/lesson", "GET", params={
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic"
    })
    
    # Test 10: Complete lesson
    print("\n📊 Test 10: Complete Lesson")
    test_api("/api/progress/complete-lesson", "POST", {
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic"
    })
    
    # Test 11: Get subject progress
    print("\n📊 Test 11: Get Subject Progress (Grade 5 Math)")
    test_api("/api/progress/subject", "GET", params={
        "user_id": USER_ID,
        "grade": "grade_5",
        "subject": "math"
    })
    
    # Test 12: Get dashboard stats
    print("\n📊 Test 12: Get Dashboard Stats")
    test_api("/api/progress/dashboard", "GET", params={
        "user_id": USER_ID
    })
    
    # Test 13: Get complete user progress
    print("\n📊 Test 13: Get Complete User Progress")
    result = test_api("/api/progress/user", "GET", params={
        "user_id": USER_ID
    })
    
    if result and result.get("code") == 0:
        print("\n" + "="*60)
        print("📈 Progress Summary")
        print("="*60)
        stats = result["data"]["progress"]["stats"]
        print(f"Lessons Started: {stats['total_lessons_started']}")
        print(f"Lessons Completed: {stats['total_lessons_completed']}")
        print(f"Sections Completed: {stats['total_sections_completed']}")
        print(f"Questions Answered: {stats['total_questions_answered']}")
        print(f"Questions Correct: {stats['total_questions_correct']}")
        print(f"Accuracy: {round(stats['total_questions_correct']/stats['total_questions_answered']*100, 1)}%")
        print(f"Time Spent: {stats['total_time_minutes']} minutes")
    
    # Test 14: Check prerequisites
    print("\n📊 Test 14: Check Prerequisites")
    test_api("/api/progress/check-prerequisites", "GET", params={
        "user_id": USER_ID,
        "prerequisites": "fractions_basic,geometry_intro"
    })
    
    print("\n" + "="*60)
    print("✅ Progress Tracking Tests Complete!")
    print("="*60 + "\n")
    
    print("💡 Check the user_progress folder to see the saved data!")
    print(f"   File: user_progress/{USER_ID.replace('/', '_')}.json")

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║  Progress Tracking System Test Suite                 ║
    ║  Make sure Flask server is running on localhost:5000 ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running!\n")
            main()
        else:
            print("❌ Server returned unexpected status")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running!")
        print("Start it with: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")
