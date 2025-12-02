"""
Lesson Manager - Load and manage lessons from JSON files
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class LessonManager:
    """Manages loading and accessing lesson data"""
    
    def __init__(self, lessons_dir: str = None):
        if lessons_dir is None:
            # Default to lessons directory relative to this file
            base_dir = Path(__file__).parent.parent
            lessons_dir = base_dir / "lessons"
        
        self.lessons_dir = Path(lessons_dir)
        self.metadata_file = self.lessons_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load the metadata.json file"""
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_file}")
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_grades(self) -> List[Dict]:
        """Get list of all available grades"""
        grades = []
        for grade_id, grade_data in self.metadata['grades'].items():
            grades.append({
                'id': grade_id,
                'name': grade_data['name'],
                'subjects': list(grade_data['subjects'].keys())
            })
        return grades
    
    def get_subjects(self, grade: str) -> List[Dict]:
        """Get all subjects for a specific grade"""
        if grade not in self.metadata['grades']:
            return []
        
        subjects = []
        for subject_id, subject_data in self.metadata['grades'][grade]['subjects'].items():
            subjects.append({
                'id': subject_id,
                'name': subject_data['name'],
                'lesson_count': len(subject_data['lessons'])
            })
        return subjects
    
    def get_lessons(self, grade: str, subject: str) -> List[Dict]:
        """Get all lessons for a specific grade and subject"""
        if grade not in self.metadata['grades']:
            return []
        
        if subject not in self.metadata['grades'][grade]['subjects']:
            return []
        
        return self.metadata['grades'][grade]['subjects'][subject]['lessons']
    
    def get_lesson(self, grade: str, subject: str, lesson_id: str) -> Optional[Dict]:
        """Load a specific lesson file"""
        lessons = self.get_lessons(grade, subject)
        
        # Find lesson in metadata
        lesson_meta = None
        for lesson in lessons:
            if lesson['id'] == lesson_id:
                lesson_meta = lesson
                break
        
        if not lesson_meta:
            return None
        
        # Load lesson file
        lesson_file = self.lessons_dir.parent / lesson_meta['file']
        
        if not lesson_file.exists():
            return None
        
        with open(lesson_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_section(self, grade: str, subject: str, lesson_id: str, section_id: str) -> Optional[Dict]:
        """Get a specific section from a lesson"""
        lesson = self.get_lesson(grade, subject, lesson_id)
        
        if not lesson:
            return None
        
        for section in lesson.get('sections', []):
            if section['id'] == section_id:
                return section
        
        return None
    
    def get_question(self, grade: str, subject: str, lesson_id: str, section_id: str, question_id: str) -> Optional[Dict]:
        """Get a specific question from a section"""
        section = self.get_section(grade, subject, lesson_id, section_id)
        
        if not section:
            return None
        
        for question in section.get('questions', []):
            if question['id'] == question_id:
                return question
        
        return None
    
    def check_prerequisites(self, grade: str, subject: str, lesson_id: str, completed_lessons: List[str]) -> bool:
        """Check if all prerequisites for a lesson are completed"""
        lesson = self.get_lesson(grade, subject, lesson_id)
        
        if not lesson:
            return False
        
        prerequisites = lesson.get('prerequisites', [])
        
        # All prerequisites must be in completed_lessons
        return all(prereq in completed_lessons for prereq in prerequisites)
    
    def get_next_lessons(self, grade: str, subject: str, lesson_id: str) -> List[Dict]:
        """Get recommended next lessons after completing this one"""
        lesson = self.get_lesson(grade, subject, lesson_id)
        
        if not lesson:
            return []
        
        next_lesson_ids = lesson.get('next_lessons', [])
        next_lessons = []
        
        for next_id in next_lesson_ids:
            next_lesson = self.get_lesson(grade, subject, next_id)
            if next_lesson:
                next_lessons.append({
                    'id': next_lesson['id'],
                    'title': next_lesson['title'],
                    'difficulty': next_lesson['difficulty'],
                    'estimated_time_minutes': next_lesson['estimated_time_minutes']
                })
        
        return next_lessons
    
    def search_lessons(self, query: str) -> List[Dict]:
        """Search for lessons by title or keywords"""
        results = []
        query_lower = query.lower()
        
        for grade_id, grade_data in self.metadata['grades'].items():
            for subject_id, subject_data in grade_data['subjects'].items():
                for lesson in subject_data['lessons']:
                    if query_lower in lesson['title'].lower() or query_lower in lesson['id'].lower():
                        results.append({
                            'grade': grade_id,
                            'grade_name': grade_data['name'],
                            'subject': subject_id,
                            'subject_name': subject_data['name'],
                            **lesson
                        })
        
        return results


# Global instance
lesson_manager = LessonManager()
