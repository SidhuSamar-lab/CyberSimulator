"""
CyberSimulator - Quiz Evaluation & Persistence Service.
Encapsulates quiz session generation, answer grading, database transactions, and AI feedback.
"""
import logging
from typing import Dict, List, Any, Tuple
from django.db import transaction
from django.utils import timezone
from users.models import Student
from quizzes.models import QuizAttempt, AttemptQuestion
from quizzes.topics import get_topic_by_id, CYBER_TOPICS
from quizzes.ai_service import ai_client

logger = logging.getLogger(__name__)


class QuizService:
    """Core domain service for quiz delivery, evaluation, and record keeping."""

    DEFAULT_QUESTIONS_COUNT: int = 3
    PASSING_THRESHOLD: float = 66.0  # 66% minimum for mastery distinction

    @classmethod
    def get_questions_for_topic(cls, topic_id: str, count: int = DEFAULT_QUESTIONS_COUNT) -> List[Dict[str, Any]]:
        """
        Retrieves scenario questions for a topic.
        Queries Azure AI Foundry (CyberQuizAgent gpt-5) with graceful fallback to curated bank.
        """
        topic = get_topic_by_id(topic_id)
        if not topic:
            logger.warning(f"Topic {topic_id} not found; falling back to default topic {CYBER_TOPICS[0]['id']}")
            topic_id = CYBER_TOPICS[0]["id"]
            topic = CYBER_TOPICS[0]

        try:
            questions = ai_client.generate_quiz_questions(topic_id=topic_id, count=count)
            if questions and len(questions) >= count:
                return questions[:count]
        except Exception as exc:
            logger.error(f"Error fetching questions from AI service: {exc}", exc_info=True)

        # Fallback to curated question pool
        from quizzes.ai_service import FALLBACK_QUESTIONS
        fallback_pool = list(FALLBACK_QUESTIONS.get(topic_id, []))
        if not fallback_pool:
            fallback_pool = list(FALLBACK_QUESTIONS.get("phishing", []))
        return fallback_pool[:count]

    @classmethod
    def grade_answers(
        cls,
        questions: List[Dict[str, Any]],
        student_answers: Dict[str, str]
    ) -> Tuple[int, int, float, List[Dict[str, Any]]]:
        """
        Pure function evaluating student answers against questions.
        Returns: (score, total, percentage, items_review)
        """
        score = 0
        total = len(questions)
        items_review = []

        for idx, q_data in enumerate(questions, start=1):
            key = str(idx)
            selected_raw = student_answers.get(key, "").strip().upper()
            correct_raw = str(q_data.get("correct_option", "")).strip().upper()

            is_correct = (selected_raw == correct_raw)
            if is_correct:
                score += 1

            items_review.append({
                "question_number": idx,
                "question_text": q_data.get("question_text", ""),
                "selected_option": selected_raw,
                "student_selected": selected_raw,
                "correct_option": correct_raw,
                "is_correct": is_correct,
                "option_a": q_data.get("option_a", ""),
                "option_b": q_data.get("option_b", ""),
                "option_c": q_data.get("option_c", ""),
                "option_d": q_data.get("option_d", ""),
                "explanation": q_data.get("explanation", ""),
            })

        percentage = round((score / total) * 100, 1) if total > 0 else 0.0
        return score, total, percentage, items_review

    @classmethod
    def save_quiz_attempt(
        cls,
        student: Student,
        topic_id: str,
        topic_title: str,
        questions: List[Dict[str, Any]],
        student_answers: Dict[str, str],
        ai_feedback_text: str = ""
    ) -> Tuple[QuizAttempt, List[Dict[str, Any]]]:
        """
        Grades answers and persists QuizAttempt and AttemptQuestion models atomically.
        """
        score, total, percentage, items_review = cls.grade_answers(questions, student_answers)

        with transaction.atomic():
            attempt = QuizAttempt.objects.create(
                student=student,
                topic_id=topic_id,
                topic_title=topic_title,
                score=score,
                total_questions=total,
                ai_feedback=ai_feedback_text,
            )

            question_records = [
                AttemptQuestion(
                    attempt=attempt,
                    question_text=item["question_text"],
                    option_a=item["option_a"],
                    option_b=item["option_b"],
                    option_c=item["option_c"],
                    option_d=item["option_d"],
                    correct_option=item["correct_option"],
                    student_answer=item["selected_option"],
                    is_correct=item["is_correct"],
                    explanation=item["explanation"],
                )
                for item in items_review
            ]
            AttemptQuestion.objects.bulk_create(question_records)

        return attempt, items_review

    @classmethod
    def generate_ai_feedback(
        cls,
        student_name: str,
        topic_title: str,
        score: int,
        total: int,
        items_review: List[Dict[str, Any]]
    ) -> str:
        """Generates supportive, personalized feedback via CyberQuizAgent with offline fallback."""
        try:
            return ai_client.generate_feedback(
                student_name=student_name,
                topic_title=topic_title,
                score=score,
                total=total,
                items_review=items_review
            )
        except Exception as exc:
            logger.error(f"Failed to query AI feedback: {exc}")
            percentage = round((score / total) * 100) if total > 0 else 0
            if percentage >= 66:
                return (
                    f"Outstanding work, Cadet {student_name}! You scored {score}/{total} ({percentage}%) on {topic_title}. "
                    "Your situational awareness in recognizing digital deception is sharp and reliable. "
                    "Rule 1: Always verify surprising messages through official channels. "
                    "Rule 2: Never share security codes or credentials."
                )
            else:
                return (
                    f"Good effort, Cadet {student_name}! You completed {topic_title} with {score}/{total}. "
                    "Cyber attackers rely on urgency and curiosity to trick people. "
                    "Take a moment to review the explanations above and try the drill again to earn your distinction badge!"
                )

    @classmethod
    def get_hint(cls, topic_title: str, question_text: str) -> str:
        """Retrieves a pedagogical hint guiding the student without giving away the answer."""
        try:
            return ai_client.generate_hint(topic_title=topic_title, question_text=question_text)
        except Exception as exc:
            logger.warning(f"AI hint service unavailable: {exc}")
            return "Look carefully for signs of pressure, urgency, unexpected links, or requests for private data."
