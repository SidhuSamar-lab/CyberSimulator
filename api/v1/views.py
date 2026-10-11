"""
CyberSimulator - Scalable RESTful API v1 View Handlers.
Features standardized JSON envelopes, robust error handling, and separation of business logic.
"""
import json
import logging
from typing import Any, Dict, Optional
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from users.models import Student
from quizzes.models import QuizAttempt
from quizzes.topics import CYBER_TOPICS, get_topic_by_id
from quizzes.services.quiz_service import QuizService
from quizzes.services.analytics_service import AnalyticsService
from quizzes.services.badge_service import BadgeService
from config.env import AppConfig
from config.supabase_client import is_supabase_configured

logger = logging.getLogger(__name__)


def api_response(data: Any, status: int = 200) -> JsonResponse:
    """Standardized API success response wrapper."""
    return JsonResponse({
        "success": True,
        "data": data,
    }, status=status)


def api_error(message: str, code: str = "ERROR", status: int = 400, details: Optional[Dict] = None) -> JsonResponse:
    """Standardized API error response wrapper."""
    return JsonResponse({
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }, status=status)


def api_root(request: HttpRequest) -> JsonResponse:
    """API Discovery & Service Welcome Endpoint."""
    return api_response({
        "name": "CyberSimulator Core API",
        "version": "v1",
        "protocol": "RESTful JSON",
        "mission": "NIST SP 800-181 Certified K-12 Cybersecurity Education",
        "ai_engine": f"Azure AI Foundry ({AppConfig.AZURE_AI_DEPLOYMENT_NAME})",
        "endpoints": {
            "health": "/api/v1/health/",
            "topics": "/api/v1/topics/",
            "quiz_generate": "/api/v1/quiz/generate/<topic_id>/",
            "quiz_submit": "/api/v1/quiz/submit/",
            "quiz_hint": "/api/v1/quiz/hint/",
            "mentor_chat": "/api/v1/mentor/chat/",
            "teacher_analytics": "/api/v1/teacher/analytics/",
            "teacher_export_csv": "/api/v1/teacher/export-csv/",
            "leaderboard": "/api/v1/leaderboard/",
        }
    })


def api_health(request: HttpRequest) -> JsonResponse:
    """System health, database latency, and AI connectivity status."""
    db_ok = True
    try:
        connection.ensure_connection()
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        db_ok = False

    return api_response({
        "status": "healthy" if db_ok else "degraded",
        "database": {
            "connected": db_ok,
            "engine": connection.vendor,
            "supabase_configured": is_supabase_configured(),
        },
        "ai_service": {
            "configured": AppConfig.is_ai_configured(),
            "model": AppConfig.AZURE_AI_DEPLOYMENT_NAME,
        },
        "platform": "CyberSimulator 2026.1",
    })


def api_topics_list(request: HttpRequest) -> JsonResponse:
    """Returns the directory of all 8 core cybersecurity threat vectors."""
    return api_response({
        "count": len(CYBER_TOPICS),
        "topics": CYBER_TOPICS,
    })


def api_topic_detail(request: HttpRequest, topic_id: str) -> JsonResponse:
    """Returns detailed specification and concepts for a single threat vector."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        return api_error(f"Topic '{topic_id}' not found", code="TOPIC_NOT_FOUND", status=404)
    return api_response(topic)


def api_quiz_generate(request: HttpRequest, topic_id: str) -> JsonResponse:
    """Generates dynamic scenario questions for the requested topic."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        return api_error(f"Topic '{topic_id}' not found", code="TOPIC_NOT_FOUND", status=404)

    try:
        count = int(request.GET.get('count', 3))
    except ValueError:
        count = 3

    questions = QuizService.get_questions_for_topic(topic_id=topic_id, count=count)
    return api_response({
        "topic_id": topic_id,
        "topic_title": topic["title"],
        "count": len(questions),
        "questions": questions,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_quiz_submit(request: HttpRequest) -> JsonResponse:
    """
    Evaluates quiz answers, grades attempt, generates AI feedback, and records attempt.
    Payload: {
        "student_id": 1,
        "topic_id": "phishing",
        "answers": {"1": "C", "2": "B", "3": "B"}
    }
    """
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return api_error("Invalid JSON body", code="INVALID_JSON", status=400)

    student_id = payload.get("student_id")
    topic_id = payload.get("topic_id")
    answers = payload.get("answers", {})

    if not student_id:
        return api_error("Missing 'student_id'", code="MISSING_FIELD", status=400)
    if not topic_id:
        return api_error("Missing 'topic_id'", code="MISSING_FIELD", status=400)

    student = Student.objects.filter(id=student_id).first()
    if not student:
        return api_error(f"Student with id {student_id} not found", code="STUDENT_NOT_FOUND", status=404)

    topic = get_topic_by_id(topic_id)
    topic_title = topic["title"] if topic else topic_id

    # Get active questions (from session or generated)
    active_quiz = request.session.get("active_quiz")
    if active_quiz and active_quiz.get("topic_id") == topic_id:
        questions = active_quiz.get("questions", [])
    else:
        questions = QuizService.get_questions_for_topic(topic_id, count=3)

    # Grade & save attempt
    score, total, percentage, items_review = QuizService.grade_answers(questions, answers)
    ai_feedback = QuizService.generate_ai_feedback(student.name, topic_title, score, total, items_review)

    attempt, _ = QuizService.save_quiz_attempt(
        student=student,
        topic_id=topic_id,
        topic_title=topic_title,
        questions=questions,
        student_answers=answers,
        ai_feedback_text=ai_feedback
    )

    request.session.pop("active_quiz", None)

    return api_response({
        "attempt_id": attempt.id,
        "student_id": student.id,
        "student_name": student.name,
        "topic_id": topic_id,
        "score": score,
        "total": total,
        "percentage": percentage,
        "passed": percentage >= 66.0,
        "ai_feedback": ai_feedback,
        "items_review": items_review,
    }, status=201)


def api_quiz_hint(request: HttpRequest) -> JsonResponse:
    """Retrieves an educational tutor hint for an active question."""
    topic_id = request.GET.get("topic_id", "phishing")
    question_text = request.GET.get("q_text", "")
    
    topic = get_topic_by_id(topic_id)
    topic_title = topic["title"] if topic else "Cybersecurity Drill"

    hint = QuizService.get_hint(topic_title=topic_title, question_text=question_text)
    return api_response({
        "topic": topic_title,
        "hint": hint,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_mentor_chat(request: HttpRequest) -> JsonResponse:
    """Interactive consultation with CyberQuizAgent (GPT-5)."""
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return api_error("Invalid JSON body", code="INVALID_JSON", status=400)

    user_message = payload.get("message", "").strip()
    topic_title = payload.get("topic_title", "Cybersecurity Safety")
    history = payload.get("history", [])

    if not user_message:
        return api_error("Message cannot be empty", code="EMPTY_MESSAGE", status=400)

    from quizzes.ai_service import ai_client
    student_name = "Cadet"
    student_id = request.session.get("student_id")
    if student_id:
        student = Student.objects.filter(id=student_id).first()
        if student:
            student_name = student.name

    reply = ai_client.chat_with_mentor(
        student_name=student_name,
        topic_title=topic_title,
        user_message=user_message,
        history=history,
    )

    return api_response({
        "reply": reply,
        "student_name": student_name,
        "model": "CyberQuizAgent (gpt-5)",
    })


def api_teacher_analytics(request: HttpRequest) -> JsonResponse:
    """Aggregated class analytics, weakness alarms, and topic breakdown."""
    metrics = AnalyticsService.get_teacher_overview_metrics()
    return api_response(metrics)


def api_teacher_export_csv(request: HttpRequest) -> HttpResponse:
    """Streams full CSV telemetry report for institutional LMS audits."""
    csv_content = AnalyticsService.generate_csv_telemetry_export()
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cybersimulator_audit_report.csv"'
    return response


def api_leaderboard(request: HttpRequest) -> JsonResponse:
    """Inter-class cohort standings and student hall of fame rankings."""
    class_names = Student.objects.values_list('class_name', flat=True).distinct()
    class_rankings = []

    for c_name in class_names:
        students = Student.objects.filter(class_name=c_name)
        attempts = QuizAttempt.objects.filter(student__in=students)
        total_attempts = attempts.count()
        total_possible = sum(a.total_questions for a in attempts)
        total_score = sum(a.score for a in attempts)
        avg_score = round((total_score / total_possible * 100), 1) if total_possible > 0 else 0.0

        class_rankings.append({
            "class_name": c_name,
            "student_count": students.count(),
            "attempts_count": total_attempts,
            "avg_accuracy": avg_score,
        })

    class_rankings.sort(key=lambda x: (x["avg_accuracy"], x["attempts_count"]), reverse=True)

    top_cadets = Student.objects.all().prefetch_related('attempts')
    sorted_cadets = sorted(top_cadets, key=lambda s: (s.average_score, s.total_attempts), reverse=True)[:10]

    cadets_list = [
        {
            "id": s.id,
            "name": s.name,
            "class_name": s.class_name,
            "roll_number": s.roll_number,
            "rank_title": s.rank_title,
            "total_attempts": s.total_attempts,
            "average_score": s.average_score,
            "badges_count": len(s.badges_earned),
        }
        for s in sorted_cadets
    ]

    return api_response({
        "class_rankings": class_rankings,
        "top_cadets": cadets_list,
    })
