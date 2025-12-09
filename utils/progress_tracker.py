"""
Progress Tracker - Track student learning progress
Stores progress in JSON files (can be upgraded to database later)
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ProgressTracker:
    """Manages student progress tracking"""
    
    def __init__(self, progress_dir: str = None):
        if progress_dir is None:
            base_dir = Path(__file__).parent.parent
            progress_dir = base_dir / "user_progress"
        
        self.progress_dir = Path(progress_dir)
        self.progress_dir.mkdir(exist_ok=True)
    
    def _get_user_file(self, user_id: str) -> Path:
        """Get path to user's progress file"""
        # Sanitize user_id for filename
        safe_user_id = "".join(c if c.isalnum() or c in '-_' else '_' for c in user_id)
        return self.progress_dir / f"{safe_user_id}.json"
    
    def _load_user_progress(self, user_id: str) -> Dict:
        """Load user's progress from file"""
        user_file = self._get_user_file(user_id)
        
        if not user_file.exists():
            # Create new progress file
            return {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "lessons": {},  # lesson_id -> lesson progress
                "stats": {
                    "total_lessons_started": 0,
                    "total_lessons_completed": 0,
                    "total_sections_completed": 0,
                    "total_questions_answered": 0,
                    "total_questions_correct": 0,
                    "total_time_minutes": 0
                }
            }
        
        with open(user_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_user_progress(self, user_id: str, progress: Dict):
        """Save user's progress to file"""
        progress["last_active"] = datetime.now().isoformat()
        user_file = self._get_user_file(user_id)
        
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    
    def start_lesson(self, user_id: str, grade: str, subject: str, lesson_id: str):
        """Mark a lesson as started"""
        progress = self._load_user_progress(user_id)
        
        lesson_key = f"{grade}/{subject}/{lesson_id}"
        
        if lesson_key not in progress["lessons"]:
            progress["lessons"][lesson_key] = {
                "grade": grade,
                "subject": subject,
                "lesson_id": lesson_id,
                "status": "in_progress",
                "started_at": datetime.now().isoformat(),
                "completed_at": None,
                "current_section": None,
                "sections_completed": [],
                "questions_answered": {},  # question_id -> {correct, attempts, hints_used}
                "total_score": 0,
                "total_questions": 0,
                "time_spent_minutes": 0
            }
            progress["stats"]["total_lessons_started"] += 1
        
        self._save_user_progress(user_id, progress)
        return progress["lessons"][lesson_key]
    
    def update_section_progress(self, user_id: str, grade: str, subject: str, 
                                lesson_id: str, section_id: str, status: str = "in_progress"):
        """Update progress for a section"""
        progress = self._load_user_progress(user_id)
        lesson_key = f"{grade}/{subject}/{lesson_id}"
        
        if lesson_key not in progress["lessons"]:
            self.start_lesson(user_id, grade, subject, lesson_id)
            progress = self._load_user_progress(user_id)
        
        lesson_progress = progress["lessons"][lesson_key]
        lesson_progress["current_section"] = section_id
        
        if status == "completed" and section_id not in lesson_progress["sections_completed"]:
            lesson_progress["sections_completed"].append(section_id)
            progress["stats"]["total_sections_completed"] += 1
        
        self._save_user_progress(user_id, progress)
        return lesson_progress
    
    def record_answer(self, user_id: str, grade: str, subject: str, lesson_id: str,
                     question_id: str, is_correct: bool, hints_used: int = 0):
        """Record a question answer"""
        progress = self._load_user_progress(user_id)
        lesson_key = f"{grade}/{subject}/{lesson_id}"
        
        if lesson_key not in progress["lessons"]:
            self.start_lesson(user_id, grade, subject, lesson_id)
            progress = self._load_user_progress(user_id)
        
        lesson_progress = progress["lessons"][lesson_key]
        
        if question_id not in lesson_progress["questions_answered"]:
            lesson_progress["questions_answered"][question_id] = {
                "correct": False,
                "attempts": 0,
                "hints_used": 0,
                "first_attempt_correct": False,
                "answered_at": None
            }
        
        question_progress = lesson_progress["questions_answered"][question_id]
        question_progress["attempts"] += 1
        question_progress["hints_used"] = max(question_progress["hints_used"], hints_used)
        
        if is_correct and not question_progress["correct"]:
            question_progress["correct"] = True
            question_progress["answered_at"] = datetime.now().isoformat()
            
            if question_progress["attempts"] == 1 and hints_used == 0:
                question_progress["first_attempt_correct"] = True
            
            # Update stats
            progress["stats"]["total_questions_correct"] += 1
        
        progress["stats"]["total_questions_answered"] += 1
        
        self._save_user_progress(user_id, progress)
        return question_progress
    
    def complete_lesson(self, user_id: str, grade: str, subject: str, lesson_id: str):
        """Mark a lesson as completed"""
        progress = self._load_user_progress(user_id)
        lesson_key = f"{grade}/{subject}/{lesson_id}"
        
        if lesson_key not in progress["lessons"]:
            return None
        
        lesson_progress = progress["lessons"][lesson_key]
        
        if lesson_progress["status"] != "completed":
            lesson_progress["status"] = "completed"
            lesson_progress["completed_at"] = datetime.now().isoformat()
            
            # Calculate score
            total_questions = len(lesson_progress["questions_answered"])
            correct_questions = sum(1 for q in lesson_progress["questions_answered"].values() if q["correct"])
            
            lesson_progress["total_questions"] = total_questions
            lesson_progress["total_score"] = round((correct_questions / total_questions * 100) if total_questions > 0 else 0, 1)
            
            progress["stats"]["total_lessons_completed"] += 1
        
        self._save_user_progress(user_id, progress)
        return lesson_progress
    
    def get_lesson_progress(self, user_id: str, grade: str, subject: str, lesson_id: str) -> Optional[Dict]:
        """Get progress for a specific lesson"""
        progress = self._load_user_progress(user_id)
        lesson_key = f"{grade}/{subject}/{lesson_id}"
        return progress["lessons"].get(lesson_key)
    
    def get_user_progress(self, user_id: str) -> Dict:
        """Get complete user progress"""
        return self._load_user_progress(user_id)
    
    def get_completed_lessons(self, user_id: str) -> List[str]:
        """Get list of completed lesson IDs"""
        progress = self._load_user_progress(user_id)
        completed = []
        
        for lesson_key, lesson_progress in progress["lessons"].items():
            if lesson_progress["status"] == "completed":
                completed.append(lesson_progress["lesson_id"])
        
        return completed
    
    def check_prerequisites(self, user_id: str, prerequisites: List[str]) -> bool:
        """Check if user has completed all prerequisite lessons"""
        if not prerequisites:
            return True
        
        completed = self.get_completed_lessons(user_id)
        return all(prereq in completed for prereq in prerequisites)
    
    def get_subject_progress(self, user_id: str, grade: str, subject: str) -> Dict:
        """Get progress for all lessons in a subject"""
        progress = self._load_user_progress(user_id)
        
        subject_lessons = {}
        for lesson_key, lesson_progress in progress["lessons"].items():
            if lesson_progress["grade"] == grade and lesson_progress["subject"] == subject:
                subject_lessons[lesson_progress["lesson_id"]] = lesson_progress
        
        return {
            "grade": grade,
            "subject": subject,
            "lessons": subject_lessons,
            "total_lessons": len(subject_lessons),
            "completed_lessons": sum(1 for l in subject_lessons.values() if l["status"] == "completed")
        }
    
    def get_dashboard_stats(self, user_id: str) -> Dict:
        """Get user stats for dashboard"""
        progress = self._load_user_progress(user_id)
        stats = progress["stats"]
        
        # Calculate additional metrics
        accuracy = 0
        if stats["total_questions_answered"] > 0:
            accuracy = round((stats["total_questions_correct"] / stats["total_questions_answered"]) * 100, 1)
        
        completion_rate = 0
        if stats["total_lessons_started"] > 0:
            completion_rate = round((stats["total_lessons_completed"] / stats["total_lessons_started"]) * 100, 1)
        
        return {
            "user_id": user_id,
            "created_at": progress["created_at"],
            "last_active": progress["last_active"],
            "lessons_started": stats["total_lessons_started"],
            "lessons_completed": stats["total_lessons_completed"],
            "completion_rate": completion_rate,
            "sections_completed": stats["total_sections_completed"],
            "questions_answered": stats["total_questions_answered"],
            "questions_correct": stats["total_questions_correct"],
            "accuracy": accuracy,
            "time_spent_minutes": stats["total_time_minutes"]
        }
    
    def add_study_time(self, user_id: str, grade: str, subject: str, lesson_id: str, minutes: int):
        """Add study time for a lesson"""
        progress = self._load_user_progress(user_id)
        lesson_key = f"{grade}/{subject}/{lesson_id}"
        
        if lesson_key in progress["lessons"]:
            progress["lessons"][lesson_key]["time_spent_minutes"] += minutes
            progress["stats"]["total_time_minutes"] += minutes
            self._save_user_progress(user_id, progress)
    
    def reset_lesson(self, user_id: str, grade: str, subject: str, lesson_id: str):
        """Reset progress for a lesson"""
        progress = self._load_user_progress(user_id)
        lesson_key = f"{grade}/{subject}/{lesson_id}"
        
        if lesson_key in progress["lessons"]:
            del progress["lessons"][lesson_key]
            self._save_user_progress(user_id, progress)
            return True
        return False
    
    def delete_user_progress(self, user_id: str):
        """Delete all progress for a user"""
        user_file = self._get_user_file(user_id)
        if user_file.exists():
            user_file.unlink()
            return True
        return False


# Global instance
progress_tracker = ProgressTracker()
