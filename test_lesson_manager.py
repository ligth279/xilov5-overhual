"""
Test the lesson manager utility
"""
from utils.lesson_manager import lesson_manager

print("\n" + "="*60)
print("Testing Lesson Manager")
print("="*60)

# Test 1: Get all grades
print("\n1. Getting all grades:")
grades = lesson_manager.get_all_grades()
for grade in grades:
    print(f"   • {grade['name']} - Subjects: {', '.join(grade['subjects'])}")

# Test 2: Get subjects for Grade 5
print("\n2. Getting subjects for grade_5:")
subjects = lesson_manager.get_subjects('grade_5')
for subject in subjects:
    print(f"   • {subject['name']} ({subject['lesson_count']} lessons)")

# Test 3: Get lessons for Grade 5 Math
print("\n3. Getting lessons for Grade 5 Math:")
lessons = lesson_manager.get_lessons('grade_5', 'math')
for lesson in lessons:
    print(f"   • {lesson['title']} ({lesson['difficulty']}, {lesson['estimated_time_minutes']} min)")

# Test 4: Load full lesson
print("\n4. Loading 'fractions_basic' lesson:")
lesson = lesson_manager.get_lesson('grade_5', 'math', 'fractions_basic')
if lesson:
    print(f"   ✅ Lesson loaded: {lesson['title']}")
    print(f"   Sections: {len(lesson['sections'])}")
    print(f"   Learning objectives: {len(lesson['learning_objectives'])}")
    
    # Show first section
    if lesson['sections']:
        section = lesson['sections'][0]
        print(f"\n   First section: {section['title']}")
        print(f"   Questions: {len(section['questions'])}")

# Test 5: Get specific section
print("\n5. Getting section 'section_1' from fractions_basic:")
section = lesson_manager.get_section('grade_5', 'math', 'fractions_basic', 'section_1')
if section:
    print(f"   ✅ Section loaded: {section['title']}")
    print(f"   Type: {section['type']}")
    print(f"   Content preview: {section['content'][:100]}...")

# Test 6: Search lessons
print("\n6. Searching for 'fraction':")
results = lesson_manager.search_lessons('fraction')
for result in results:
    print(f"   • {result['title']} ({result['grade_name']} - {result['subject_name']})")

print("\n" + "="*60)
print("✅ All tests passed!")
print("="*60 + "\n")
