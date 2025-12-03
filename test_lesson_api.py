"""
Test Lesson API Endpoints
Run this with the Flask server running
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_api(endpoint, method="GET", data=None):
    """Helper to test API endpoints"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"{method} {endpoint}")
    print('='*60)
    
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("Testing Lesson System API Endpoints")
    print("="*60)
    
    # Test 1: Get all grades
    print("\n📚 Test 1: Get All Grades")
    test_api("/api/lessons/grades")
    
    # Test 2: Get subjects for Grade 5
    print("\n📚 Test 2: Get Subjects for Grade 5")
    test_api("/api/lessons/grade_5/subjects")
    
    # Test 3: Get lessons for Grade 5 Math
    print("\n📚 Test 3: Get Lessons for Grade 5 Math")
    test_api("/api/lessons/grade_5/math")
    
    # Test 4: Get full lesson
    print("\n📚 Test 4: Get Full Lesson (Fractions)")
    test_api("/api/lessons/grade_5/math/fractions_basic")
    
    # Test 5: Get specific section
    print("\n📚 Test 5: Get Section 1")
    test_api("/api/lessons/grade_5/math/fractions_basic/section/section_1")
    
    # Test 6: Search lessons
    print("\n📚 Test 6: Search for 'fraction'")
    test_api("/api/lessons/search?q=fraction")
    
    # Test 7: Doubt chat (requires model to be loaded)
    print("\n📚 Test 7: Doubt Clearing Chat")
    test_api("/api/lessons/doubt-chat", "POST", {
        "message": "Can you give me another example of a fraction?",
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "section_id": "section_1"
    })
    
    # Test 8: Evaluate answer (simple)
    print("\n📚 Test 8: Evaluate Answer (Simple)")
    test_api("/api/lessons/evaluate-answer", "POST", {
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "section_id": "section_1",
        "question_id": "q1",
        "answer": "numerator",
        "use_ai": False
    })
    
    # Test 9: Evaluate answer (AI)
    print("\n📚 Test 9: Evaluate Answer (AI)")
    test_api("/api/lessons/evaluate-answer", "POST", {
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "section_id": "section_1",
        "question_id": "q1",
        "answer": "the top number",
        "use_ai": True
    })
    
    # Test 10: Get hint
    print("\n📚 Test 10: Get Hint (Level 0)")
    test_api("/api/lessons/get-hint", "POST", {
        "grade": "grade_5",
        "subject": "math",
        "lesson_id": "fractions_basic",
        "section_id": "section_1",
        "question_id": "q1",
        "hint_level": 0
    })
    
    print("\n" + "="*60)
    print("✅ API Testing Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║  Lesson System API Test Suite                         ║
    ║  Make sure Flask server is running on localhost:5000  ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    try:
        # Check if server is running
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
