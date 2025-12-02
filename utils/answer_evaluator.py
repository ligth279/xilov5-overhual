"""
Answer Evaluator - Evaluate student answers using Mistral 7B and Phi-3.5
Mistral 7B: Accurate answer evaluation and hint generation
Phi-3.5: General tutoring chat
"""
from typing import Dict, List, Tuple


class AnswerEvaluator:
    """Evaluates student answers against expected answers"""
    
    def __init__(self, phi_model=None, mistral_model=None):
        """
        Initialize evaluator
        
        Args:
            phi_model: Optional Phi model instance for general chat
            mistral_model: Optional Mistral model instance for answer evaluation
        """
        self.phi_model = phi_model
        self.mistral_model = mistral_model  # Add Mistral for accurate evaluation
    
    def evaluate_simple(self, student_answer: str, evaluation_criteria: List[str]) -> Tuple[bool, float]:
        """
        Simple keyword-based evaluation
        
        Args:
            student_answer: The student's answer
            evaluation_criteria: List of acceptable answers/keywords
        
        Returns:
            (is_correct, confidence_score)
        """
        if not student_answer or not evaluation_criteria:
            return False, 0.0
        
        student_lower = student_answer.lower().strip()
        
        # Check exact matches first
        for criterion in evaluation_criteria:
            criterion_lower = criterion.lower().strip()
            
            # Exact match
            if student_lower == criterion_lower:
                return True, 1.0
            
            # Contains the criterion
            if criterion_lower in student_lower:
                return True, 0.9
        
        return False, 0.0
    
    def evaluate_with_ai(self, question: str, student_answer: str, expected_answer: str, 
                         evaluation_criteria: List[str]) -> Tuple[bool, float, str]:
        """
        AI-based evaluation using Phi-3.5
        
        Args:
            question: The original question
            student_answer: The student's answer
            expected_answer: The expected answer
            evaluation_criteria: List of acceptable answers
        
        Returns:
            (is_correct, confidence_score, feedback)
        """
        if not self.phi_model:
            # Fallback to simple evaluation
            is_correct, confidence = self.evaluate_simple(student_answer, evaluation_criteria)
            feedback = "Correct!" if is_correct else "Not quite. Try again!"
            return is_correct, confidence, feedback
        
        # First try simple matching
        is_simple_correct, simple_confidence = self.evaluate_simple(student_answer, evaluation_criteria)
        
        if is_simple_correct and simple_confidence >= 0.9:
            return True, simple_confidence, "Excellent! That's correct!"
        
        # Use AI for more nuanced evaluation
        evaluation_prompt = f"""You are evaluating a student's answer. Be encouraging but accurate.

Question: {question}
Expected Answer: {expected_answer}
Student's Answer: {student_answer}

Acceptable variations: {', '.join(evaluation_criteria)}

Evaluate if the student's answer is correct. Consider:
1. Does it match the expected answer in meaning?
2. Are there any acceptable variations or synonyms?
3. Is the core concept understood?

Respond ONLY with:
CORRECT: [brief encouraging feedback]
OR
INCORRECT: [gentle feedback explaining what's missing]

Keep feedback to 1-2 sentences."""

        try:
            # Generate evaluation
            ai_response = self.phi_model.generate_response(
                evaluation_prompt,
                temperature=0.3,
                max_tokens=100
            )
            
            response_upper = ai_response.upper()
            
            if "CORRECT:" in response_upper:
                feedback = ai_response.split("CORRECT:", 1)[1].strip()
                return True, 0.85, feedback
            elif "INCORRECT:" in response_upper:
                feedback = ai_response.split("INCORRECT:", 1)[1].strip()
                return False, 0.0, feedback
            else:
                # Fallback if AI doesn't follow format
                return is_simple_correct, simple_confidence, "Let me check that..."
                
        except Exception as e:
            print(f"AI evaluation error: {e}")
            # Fallback to simple evaluation
            feedback = "Correct!" if is_simple_correct else "Not quite right. Try again!"
            return is_simple_correct, simple_confidence, feedback
    
    def get_hint(self, question_data: Dict, hint_level: int = 0, student_answer: str = None) -> str:
        """
        Get an intelligent hint for a question based on student's answer
        
        Args:
            question_data: Question dictionary containing hints
            hint_level: Which hint to return (0 = first hint)
            student_answer: Student's actual answer (for AI-generated contextual hints)
        
        Returns:
            Hint text (generic or AI-generated based on answer)
        """
        print(f"[DEBUG] get_hint called: student_answer='{student_answer}', has_phi_model={self.phi_model is not None}")
        
        # If student provided an answer and we have Mistral, use it for accurate evaluation
        if student_answer and self.mistral_model:
            print(f"[DEBUG] Using Mistral 7B for accurate hint generation")
            return self.get_ai_hint(question_data, student_answer, hint_level)
        # Fallback to Phi if Mistral not available
        elif student_answer and self.phi_model:
            print(f"[DEBUG] Using Phi 3.5 for hint generation (fallback)")
            return self.get_ai_hint(question_data, student_answer, hint_level)
        
        print(f"[DEBUG] Using predefined hints (no answer={not student_answer}, no model available)")
        
        # Otherwise, use predefined hints
        hints = question_data.get('hints', [])
        
        if hint_level < len(hints):
            return hints[hint_level]
        else:
            return "No more hints available. Try your best!"
    
    def get_ai_hint(self, question_data: Dict, student_answer: str, hint_level: int) -> str:
        """
        Generate intelligent, contextual hint using Mistral 7B (unified approach)
        Mistral analyzes the mistake type AND generates appropriate pedagogical hint
        
        Args:
            question_data: Question dictionary with question, answer, type, context
            student_answer: What the student answered
            hint_level: Current hint level (0=subtle, 1=direct, 2=strong)
        
        Returns:
            Contextual hint based on student's mistake (never reveals answer)
        """
        question = question_data.get('question', '')
        expected_answer = question_data.get('answer', '')
        question_type = question_data.get('type', 'short_answer')
        question_context = question_data.get('context', '')
        
        # Choose model: Mistral preferred for accuracy, Phi as fallback
        model_to_use = self.mistral_model if self.mistral_model else self.phi_model
        model_name = "Mistral 7B" if self.mistral_model else "Phi 3.5"
        
        if not model_to_use or not model_to_use.is_loaded:
            print(f"[DEBUG] No AI model available for hints")
            return "Think carefully about the question. Review the material if needed."
        
        print(f"[DEBUG] Using {model_name} for unified hint generation")
        
        # PEDAGOGICAL PROMPT - Three-tier hint system based on proximity
        system_prompt = """You are a patient tutor. Analyze the student's answer and categorize it:

CATEGORY 1 - SLIGHTLY WRONG (spelling error, close variation):
- Point to the right part without revealing answer
- Example: "stanz" vs "stanza" → "You're very close! Check the spelling at the end of the word."
- Example: "photo synthesis" vs "photosynthesis" → "Almost there! This should be one word."

CATEGORY 2 - WRONG BUT ON TOPIC (related concept, but not what we're looking for):
- Explain what they wrote AND clarify what the question is asking for
- Example: "lines" vs "stanza" → "Lines are the individual rows in a poem, but we're looking for the term for a group of lines together, like a paragraph in poetry."
- Example: "evaporation" vs "condensation" → "Evaporation is when water turns to vapor, but the question asks about vapor turning back to liquid."

CATEGORY 3 - COMPLETELY UNRELATED (off-topic, random answer):
- Return EXACTLY: "UNRELATED"
- This will close the quiz and restart the lesson

Keep hints SHORT (1-2 sentences). Never reveal the answer directly."""

        user_prompt = f"""Question: {question}
Student answered: {student_answer}
Hint level: {hint_level}

Categorize and give appropriate hint:"""

        try:
            # Generate proximity-based hint
            # Different models use different parameter names (prompt vs user_message)
            try:
                # Try 'prompt' first (Mistral)
                hint = model_to_use.generate_response(
                    prompt=user_prompt,
                    max_new_tokens=100,
                    temperature=0.3,
                    top_p=0.9,
                    system_prompt_override=system_prompt
                )
            except TypeError:
                # Fallback to 'user_message' (GPT-OSS, Llama, Phi)
                hint = model_to_use.generate_response(
                    user_message=user_prompt,
                    max_new_tokens=100,
                    temperature=0.3,
                    top_p=0.9,
                    system_prompt_override=system_prompt
                )
            
            # Clean up the hint
            hint = hint.strip().strip('"\'')
            
            # Check if answer is completely unrelated
            if "UNRELATED" in hint.upper():
                return "CLOSE_QUIZ"  # Special signal to close quiz
            
            # Remove category labels from AI response (e.g., "CATEGORY 1 - SLIGHTLY WRONG")
            import re
            hint = re.sub(r'^CATEGORY \d+ - [A-Z\s]+\n?', '', hint, flags=re.IGNORECASE | re.MULTILINE)
            hint = re.sub(r'^(Hint:|HINT:)\s*', '', hint, flags=re.IGNORECASE)
            hint = re.sub(r'^\s*-\s*', '', hint)  # Remove leading dash
            hint = hint.strip()
            
            print(f"[DEBUG] Cleaned hint: {hint[:100]}...")
            
            return hint
            
        except Exception as e:
            print(f"[ERROR] Hint generation error: {e}")
            import traceback
            traceback.print_exc()
            hints = question_data.get('hints', [])
            if hint_level < len(hints):
                return hints[hint_level]
            return "Think carefully about the question. Review the material if needed."
        
        finally:
            # Cleanup after generation
            import torch
            import gc
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                gc.collect()
                torch.xpu.empty_cache()
    
    def evaluate_answer(self, question_data: Dict, student_answer: str, use_ai: bool = False) -> Dict:
        """
        Main evaluation method
        
        Args:
            question_data: Full question dictionary
            student_answer: Student's answer
            use_ai: Whether to use AI evaluation (slower but more accurate)
        
        Returns:
            Dictionary with evaluation results
        """
        evaluation_criteria = question_data.get('evaluation_criteria', [])
        expected_answer = question_data.get('answer', '')
        question = question_data.get('question', '')
        
        if use_ai and self.phi_model:
            is_correct, confidence, feedback = self.evaluate_with_ai(
                question, student_answer, expected_answer, evaluation_criteria
            )
        else:
            is_correct, confidence = self.evaluate_simple(student_answer, evaluation_criteria)
            if is_correct:
                feedback = "Excellent! That's correct! 🎉"
            else:
                feedback = "Not quite right. Would you like a hint?"
        
        return {
            'is_correct': is_correct,
            'confidence': confidence,
            'feedback': feedback,
            'expected_answer': expected_answer if not is_correct else None
        }


# Global instance (will be initialized with phi_model in app.py)
answer_evaluator = AnswerEvaluator()
