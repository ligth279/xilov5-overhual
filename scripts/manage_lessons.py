"""
Lesson Management Script
Add new lessons to the Xilo AI Tutor system
"""
import json
import os
from pathlib import Path
from datetime import datetime

# Base paths
BASE_DIR = Path(__file__).parent.parent
LESSONS_DIR = BASE_DIR / "lessons"
METADATA_FILE = LESSONS_DIR / "metadata.json"


def load_metadata():
    """Load the metadata.json file"""
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_metadata(metadata):
    """Save the metadata.json file"""
    metadata['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✅ Metadata updated: {METADATA_FILE}")


def create_lesson_template():
    """Return a template for a new lesson"""
    return {
        "id": "",
        "title": "",
        "grade": "",
        "subject": "",
        "difficulty": "beginner",
        "estimated_time_minutes": 30,
        "prerequisites": [],
        "learning_objectives": [
            "Objective 1",
            "Objective 2"
        ],
        "sections": [
            {
                "id": "section_1",
                "title": "Introduction",
                "type": "reading",
                "content": "Your content here...",
                "questions": [
                    {
                        "id": "q1",
                        "question": "Your question?",
                        "answer": "Expected answer",
                        "evaluation_criteria": ["answer", "alternative"],
                        "hints": [
                            "Hint 1",
                            "Hint 2"
                        ]
                    }
                ]
            }
        ],
        "summary": "Lesson summary...",
        "next_lessons": []
    }


def add_lesson_interactive():
    """Interactively add a new lesson"""
    print("\n" + "="*50)
    print("📚 Add New Lesson to Xilo AI Tutor")
    print("="*50 + "\n")
    
    # Load metadata
    metadata = load_metadata()
    
    # Get grade
    print("Available grades:", ", ".join(metadata['grades'].keys()))
    grade = input("Grade (e.g., grade_5): ").strip()
    
    if grade not in metadata['grades']:
        create_new = input(f"Grade '{grade}' doesn't exist. Create it? (y/n): ")
        if create_new.lower() == 'y':
            grade_name = input("Grade display name (e.g., Grade 5): ")
            metadata['grades'][grade] = {
                "name": grade_name,
                "subjects": {}
            }
    
    # Get subject
    if grade in metadata['grades']:
        subjects = metadata['grades'][grade]['subjects']
        print(f"Available subjects in {grade}:", ", ".join(subjects.keys()) if subjects else "None")
    
    subject = input("Subject (e.g., math, english, science): ").strip()
    
    if subject not in metadata['grades'][grade]['subjects']:
        create_new = input(f"Subject '{subject}' doesn't exist. Create it? (y/n): ")
        if create_new.lower() == 'y':
            subject_name = input("Subject display name (e.g., Mathematics): ")
            metadata['grades'][grade]['subjects'][subject] = {
                "name": subject_name,
                "lessons": []
            }
    
    # Get lesson info
    lesson_id = input("Lesson ID (e.g., fractions_basic): ").strip()
    lesson_title = input("Lesson Title (e.g., Introduction to Fractions): ").strip()
    difficulty = input("Difficulty (beginner/intermediate/advanced) [beginner]: ").strip() or "beginner"
    time_minutes = input("Estimated time in minutes [30]: ").strip()
    time_minutes = int(time_minutes) if time_minutes else 30
    
    # Create lesson file
    lesson_file_path = LESSONS_DIR / grade / subject / f"{lesson_id}.json"
    lesson_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create lesson from template
    lesson = create_lesson_template()
    lesson['id'] = lesson_id
    lesson['title'] = lesson_title
    lesson['grade'] = grade
    lesson['subject'] = subject
    lesson['difficulty'] = difficulty
    lesson['estimated_time_minutes'] = time_minutes
    
    # Save lesson file
    with open(lesson_file_path, 'w', encoding='utf-8') as f:
        json.dump(lesson, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Lesson file created: {lesson_file_path}")
    print(f"⚠️  Please edit the file to add content, sections, and questions!")
    
    # Update metadata
    lesson_entry = {
        "id": lesson_id,
        "title": lesson_title,
        "file": f"lessons/{grade}/{subject}/{lesson_id}.json",
        "difficulty": difficulty,
        "estimated_time_minutes": time_minutes,
        "prerequisites": []
    }
    
    metadata['grades'][grade]['subjects'][subject]['lessons'].append(lesson_entry)
    save_metadata(metadata)
    
    print("\n✅ Lesson added successfully!")
    print(f"📝 Edit your lesson at: {lesson_file_path}")


def list_lessons():
    """List all lessons in the system"""
    metadata = load_metadata()
    
    print("\n" + "="*50)
    print("📚 All Lessons in Xilo AI Tutor")
    print("="*50 + "\n")
    
    for grade_id, grade_data in metadata['grades'].items():
        print(f"\n{grade_data['name']} ({grade_id})")
        print("-" * 40)
        
        for subject_id, subject_data in grade_data['subjects'].items():
            if subject_data['lessons']:
                print(f"\n  {subject_data['name']}:")
                for lesson in subject_data['lessons']:
                    print(f"    • {lesson['title']} ({lesson['id']})")
                    print(f"      Difficulty: {lesson['difficulty']} | Time: {lesson['estimated_time_minutes']} min")
            else:
                print(f"\n  {subject_data['name']}: No lessons yet")


def main():
    """Main menu"""
    while True:
        print("\n" + "="*50)
        print("📚 Xilo Lesson Management")
        print("="*50)
        print("1. Add new lesson")
        print("2. List all lessons")
        print("3. Exit")
        
        choice = input("\nChoose an option: ").strip()
        
        if choice == "1":
            add_lesson_interactive()
        elif choice == "2":
            list_lessons()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Try again.")


if __name__ == "__main__":
    main()
