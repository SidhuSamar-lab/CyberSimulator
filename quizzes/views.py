import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count
from django.utils import timezone
from users.models import Student
from .models import QuizAttempt, AttemptQuestion
from .topics import CYBER_TOPICS, get_topic_by_id
from .ai_service import ai_client


def is_teacher(user):
    """Staff or superuser check for teacher routes."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def home(request):
    """Landing homepage presenting the platform to students and educators."""
    total_students = Student.objects.count()
    total_quizzes = QuizAttempt.objects.count()
    return render(request, 'quizzes/home.html', {
        'topics': CYBER_TOPICS,
        'total_students': total_students,
        'total_quizzes': total_quizzes,
    })


def student_dashboard(request):
    """
    Main student hub displaying the 8 cybersecurity topics,
    along with student's personal completion history and badges.
    """
    student_id = request.session.get('student_id')
    if not student_id:
        messages.info(request, "Please enter your details to access your student dashboard.")
        return redirect('student_login')

    student = get_object_or_404(Student, id=student_id)
    student_attempts = QuizAttempt.objects.filter(student=student)

    # Compute per-topic progress
    topics_with_progress = []
    for topic in CYBER_TOPICS:
        t_id = topic["id"]
        topic_attempts = student_attempts.filter(topic_id=t_id)
        has_completed = topic_attempts.exists()
        best_score = 0
        best_total = 3
        if has_completed:
            best_attempt = topic_attempts.order_by('-score').first()
            best_score = best_attempt.score
            best_total = best_attempt.total_questions

        percentage = round((best_score / best_total) * 100) if best_total > 0 and has_completed else 0
        topics_with_progress.append({
            **topic,
            'completed': has_completed,
            'is_completed': has_completed,
            'best_score': best_score,
            'best_total': best_total,
            'percentage': percentage,
            'attempts_count': topic_attempts.count(),
        })

    total_topics = len(CYBER_TOPICS)
    completed_count = sum(1 for t in topics_with_progress if t['completed'])
    completion_percentage = int((completed_count / total_topics) * 100) if total_topics else 0
    active_count = sum(1 for t in topics_with_progress if t['attempts_count'] > 0 and not t['completed'])
    pending_count = max(0, total_topics - completed_count - active_count)
    overall_percent = student.average_score
    earned_badges = student.get_earned_badges()
    unlocked_badge_count = sum(1 for b in earned_badges if b['earned'])

    # Top peer scholars in same grade for cohort standings
    top_peers = Student.objects.filter(class_name=student.class_name).exclude(id=student.id)[:2]
    top_students = []
    for peer in top_peers:
        top_students.append({
            'name': peer.name,
            'badge_count': len(peer.badges_earned),
            'total_score': peer.total_score,
        })

    return render(request, 'quizzes/student_dashboard.html', {
        'student': student,
        'topics': topics_with_progress,
        'completed_count': completed_count,
        'total_topics': total_topics,
        'completion_percentage': completion_percentage,
        'active_count': active_count,
        'pending_count': pending_count,
        'overall_percent': overall_percent,
        'top_students': top_students,
        'recent_attempts': student_attempts[:5],
        'badges': earned_badges,
        'unlocked_badge_count': unlocked_badge_count,
        'rank_title': student.rank_title,
    })


def take_quiz(request, topic_id):
    """
    Renders the active quiz for the selected topic.
    Generates 3 dynamic questions on the fly via Azure AI Foundry.
    """
    student_id = request.session.get('student_id')
    if not student_id:
        messages.warning(request, "Please log in before starting a quiz.")
        return redirect('student_login')

    student = get_object_or_404(Student, id=student_id)
    topic = get_topic_by_id(topic_id)
    if not topic:
        messages.error(request, "Invalid cybersecurity topic selected.")
        return redirect('student_dashboard')

    # Dynamically generate questions from Azure AI Foundry
    questions = ai_client.generate_quiz_questions(topic_id, count=3)

    # Cache active quiz in student's session for secure submission evaluation
    request.session['active_quiz'] = {
        'topic_id': topic_id,
        'topic_title': topic['title'],
        'questions': questions,
    }

    return render(request, 'quizzes/quiz_take.html', {
        'student': student,
        'topic': topic,
        'questions': questions,
        'total_questions': len(questions),
    })


def submit_quiz(request):
    """
    Evaluates student quiz answers, queries Azure AI Foundry for personalized review,
    and saves the attempt and questions to the database.
    """
    student_id = request.session.get('student_id')
    if not student_id or request.method != 'POST':
        return redirect('student_dashboard')

    student = get_object_or_404(Student, id=student_id)
    active_quiz = request.session.get('active_quiz')

    if not active_quiz:
        messages.error(request, "Quiz session expired or not found. Please restart the quiz.")
        return redirect('student_dashboard')

    topic_id = active_quiz['topic_id']
    topic_title = active_quiz['topic_title']
    questions = active_quiz['questions']

    score = 0
    total = len(questions)
    items_review = []
    question_records = []

    for idx, q_data in enumerate(questions, start=1):
        selected_option = request.POST.get(f'q_{idx}', '').strip().upper()
        correct_option = q_data.get('correct_option', '').strip().upper()
        is_correct = (selected_option == correct_option)

        if is_correct:
            score += 1

        review_item = {
            'question_text': q_data.get('question_text', ''),
            'student_selected': selected_option,
            'correct_option': correct_option,
            'is_correct': is_correct,
            'explanation': q_data.get('explanation', ''),
        }
        items_review.append(review_item)

        question_records.append({
            'question_number': idx,
            'question_text': q_data.get('question_text', ''),
            'option_a': q_data.get('option_a', ''),
            'option_b': q_data.get('option_b', ''),
            'option_c': q_data.get('option_c', ''),
            'option_d': q_data.get('option_d', ''),
            'correct_option': correct_option,
            'student_selected_option': selected_option,
            'is_correct': is_correct,
            'explanation': q_data.get('explanation', ''),
        })

    # Call Azure AI Foundry for educational mentor review
    ai_feedback = ai_client.generate_feedback(
        student_name=student.name,
        topic_title=topic_title,
        score=score,
        total=total,
        items_review=items_review
    )

    # Save to database
    attempt = QuizAttempt.objects.create(
        student=student,
        topic_id=topic_id,
        topic_title=topic_title,
        score=score,
        total_questions=total,
        ai_feedback=ai_feedback,
    )

    for q_rec in question_records:
        AttemptQuestion.objects.create(
            attempt=attempt,
            **q_rec
        )

    # Clear cached quiz from session
    request.session.pop('active_quiz', None)

    return redirect('quiz_result', attempt_id=attempt.id)


def quiz_result(request, attempt_id):
    """
    Renders detailed results for a quiz attempt, including AI mentor feedback.
    """
    student_id = request.session.get('student_id')
    is_teacher_user = is_teacher(request.user)

    attempt = get_object_or_404(QuizAttempt, id=attempt_id)

    # Verify authorization: must be either the student who took it or a teacher
    if not is_teacher_user and attempt.student.id != student_id:
        messages.error(request, "You are not authorized to view this result.")
        return redirect('student_dashboard')

    topic = get_topic_by_id(attempt.topic_id)
    questions = attempt.questions.all().order_by('question_number')

    return render(request, 'quizzes/quiz_result.html', {
        'attempt': attempt,
        'topic': topic,
        'questions': questions,
        'is_teacher': is_teacher_user,
    })


@user_passes_test(is_teacher, login_url='teacher_login')
def teacher_dashboard(request):
    """
    Teacher & Administrator Dashboard featuring class-wide Chart.js analytics,
    weakest topic breakdown, and filterable student roster.
    """
    total_students = Student.objects.count()
    total_attempts = QuizAttempt.objects.count()

    overall_avg_raw = QuizAttempt.objects.aggregate(Avg('percentage'))['percentage__avg']
    overall_avg = round(overall_avg_raw, 1) if overall_avg_raw is not None else 0.0

    # Get distinct classes for filter dropdown
    classes = Student.objects.values_list('class_name', flat=True).distinct().order_by('class_name')

    # Topic performance statistics
    topic_stats = []
    for topic in CYBER_TOPICS:
        t_attempts = QuizAttempt.objects.filter(topic_id=topic['id'])
        t_count = t_attempts.count()
        t_avg_raw = t_attempts.aggregate(Avg('percentage'))['percentage__avg']
        t_avg = round(t_avg_raw, 1) if t_avg_raw is not None else None

        topic_stats.append({
            'id': topic['id'],
            'title': topic['title'],
            'attempts_count': t_count,
            'average_percentage': t_avg,
        })

    # Identify weakest topic (among topics that have attempts)
    attempted_topics = [t for t in topic_stats if t['average_percentage'] is not None]
    weakest_topic = min(attempted_topics, key=lambda x: x['average_percentage']) if attempted_topics else None

    # Search and Filter on Student Roster
    search_query = request.GET.get('q', '').strip()
    selected_class = request.GET.get('class_name', '').strip()

    students_qs = Student.objects.all().prefetch_related('attempts')
    if selected_class:
        students_qs = students_qs.filter(class_name=selected_class)
    if search_query:
        students_qs = students_qs.filter(name__icontains=search_query) | students_qs.filter(roll_number__icontains=search_query)

    students = list(students_qs)

    # Recent attempts across all students
    recent_attempts = QuizAttempt.objects.select_related('student').all()[:8]

    return render(request, 'teachers/dashboard.html', {
        'total_students': total_students,
        'total_attempts': total_attempts,
        'overall_avg': overall_avg,
        'topic_stats': topic_stats,
        'weakest_topic': weakest_topic,
        'classes': classes,
        'selected_class': selected_class,
        'search_query': search_query,
        'students': students,
        'recent_attempts': recent_attempts,
    })


@user_passes_test(is_teacher, login_url='teacher_login')
def teacher_student_detail(request, student_id):
    """
    Detailed inspection of a specific student:
    all quiz attempts, average scores, and progress across the 8 topics.
    """
    student = get_object_or_404(Student, id=student_id)
    attempts = student.attempts.all().order_by('-completed_at')

    # Topic coverage for this student
    topic_breakdown = []
    for topic in CYBER_TOPICS:
        t_attempts = attempts.filter(topic_id=topic['id'])
        has_taken = t_attempts.exists()
        best_score = 0
        if has_taken:
            best_score = t_attempts.order_by('-score').first().score

        topic_breakdown.append({
            'topic': topic,
            'taken': has_taken,
            'attempts_count': t_attempts.count(),
            'best_score': best_score,
        })

    return render(request, 'teachers/student_detail.html', {
        'student': student,
        'attempts': attempts,
        'topic_breakdown': topic_breakdown,
    })


@user_passes_test(is_teacher, login_url='teacher_login')
def teacher_analytics_api(request):
    """
    API returning Chart.js ready JSON data, with optional class filter.
    """
    selected_class = request.GET.get('class_name', '').strip()
    attempts_qs = QuizAttempt.objects.all()

    if selected_class:
        attempts_qs = attempts_qs.filter(student__class_name=selected_class)

    labels = []
    averages = []
    attempt_counts = []

    for topic in CYBER_TOPICS:
        labels.append(topic['title'])
        t_attempts = attempts_qs.filter(topic_id=topic['id'])
        avg_val = t_attempts.aggregate(Avg('percentage'))['percentage__avg']
        averages.append(round(avg_val, 1) if avg_val is not None else 0)
        attempt_counts.append(t_attempts.count())

    return JsonResponse({
        'labels': labels,
        'averages': averages,
        'attempt_counts': attempt_counts,
    })


@user_passes_test(is_teacher, login_url='teacher_login')
def teacher_export_csv(request):
    """
    Exports student quiz results into a downloadable CSV report.
    Allows filtering by class name.
    """
    import csv
    from django.http import HttpResponse

    selected_class = request.GET.get('class_name', '').strip()
    attempts_qs = QuizAttempt.objects.select_related('student').all()
    if selected_class:
        attempts_qs = attempts_qs.filter(student__class_name=selected_class)

    filename = f"cybersimulator_report_{selected_class or 'all_classes'}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Student Name', 'Class', 'Roll Number', 'Topic',
        'Score', 'Total Questions', 'Percentage', 'Completed At (UTC)', 'AI Mentor Review Excerpt'
    ])

    for att in attempts_qs:
        feedback_snippet = (att.ai_feedback[:120] + '...') if len(att.ai_feedback) > 120 else att.ai_feedback
        clean_snippet = feedback_snippet.replace('\n', ' ')
        writer.writerow([
            att.student.name,
            att.student.class_name,
            att.student.roll_number,
            att.topic_title,
            att.score,
            att.total_questions,
            f"{att.percentage}%",
            att.completed_at.strftime('%Y-%m-%d %H:%M:%S'),
            clean_snippet,
        ])

    return response


def get_quiz_hint(request):
    """
    Provides an encouraging, educational AI hint for a question during an active quiz.
    Uses student's active_quiz session.
    """
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    active_quiz = request.session.get('active_quiz')
    if not active_quiz:
        return JsonResponse({'error': 'No active quiz found'}, status=404)

    try:
        q_num = int(request.GET.get('q', 1))
        questions = active_quiz.get('questions', [])
        if 1 <= q_num <= len(questions):
            q_data = questions[q_num - 1]
            explanation = q_data.get('explanation', '')
            hint_text = f"💡 AI Tutor Hint: Focus on the key danger—{explanation}"
            return JsonResponse({'hint': hint_text})
        return JsonResponse({'error': 'Invalid question index'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def health_check(request):
    """
    System and cloud health check endpoint for monitoring & uptime.
    """
    from django.db import connection
    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    return JsonResponse({
        'status': 'healthy' if db_ok else 'degraded',
        'database': 'connected' if db_ok else 'error',
        'ai_agent': 'CyberQuizAgent (gpt-5)',
        'platform': 'CyberSimulator v1.0',
    })




def chat_mentor_api(request):
    """
    POST API for interactive live AI consultation with CyberQuizAgent (GPT-5).
    Payload: { "message": "...", "topic_title": "...", "history": [...] }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        topic_title = data.get('topic_title', 'Cybersecurity Safety')
        history = data.get('history', [])

        if not message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        student_name = "Student"
        student_id = request.session.get('student_id')
        if student_id:
            student = Student.objects.filter(id=student_id).first()
            if student:
                student_name = student.name

        reply = ai_client.chat_with_mentor(
            student_name=student_name,
            topic_title=topic_title,
            user_message=message,
            history=history,
        )

        return JsonResponse({
            'reply': reply,
            'student_name': student_name,
            'model': 'CyberQuizAgent (gpt-5)'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def leaderboard_view(request):
    """
    Inter-Class Competition & Student Hall of Fame Leaderboard.
    Aggregates performance by class section (e.g., Grade 9-A vs 9-B),
    as well as top individual cyber defense scores.
    """
    student_id = request.session.get('student_id')
    current_student = Student.objects.filter(id=student_id).first() if student_id else None

    # Distinct class sections
    class_names = Student.objects.values_list('class_name', flat=True).distinct()
    class_rankings = []

    for c_name in class_names:
        students_in_class = Student.objects.filter(class_name=c_name)
        student_count = students_in_class.count()
        attempts_in_class = QuizAttempt.objects.filter(student__in=students_in_class)
        attempts_count = attempts_in_class.count()

        if attempts_count > 0:
            avg_acc = attempts_in_class.aggregate(Avg('percentage'))['percentage__avg'] or 0.0
            avg_acc = round(avg_acc, 1)
        else:
            avg_acc = 0.0

        class_rankings.append({
            'class_name': c_name,
            'student_count': student_count,
            'attempts_count': attempts_count,
            'avg_accuracy': avg_acc,
        })

    # Sort classes by avg_accuracy descending, then by attempts_count descending
    class_rankings.sort(key=lambda c: (c['avg_accuracy'], c['attempts_count']), reverse=True)

    # Top individual students
    all_students = Student.objects.annotate(
        num_attempts=Count('attempts'),
        calculated_avg=Avg('attempts__percentage')
    ).filter(num_attempts__gt=0).order_by('-calculated_avg', '-num_attempts')[:10]

    top_students = []
    for s in all_students:
        top_students.append({
            'student': s,
            'rank_title': s.rank_title,
            'earned_badges_count': sum(1 for b in s.get_earned_badges() if b['earned']),
            'total_attempts': s.num_attempts,
            'avg_score': round(s.calculated_avg or 0.0, 1),
        })

    return render(request, 'quizzes/leaderboard.html', {
        'class_rankings': class_rankings,
        'top_students': top_students,
        'current_student': current_student,
    })


def student_certificate(request):
    """
    Generates a personalized, print-ready Certificate of Cyber Mastery.
    Features cryptographic verification hash, seal, student rank, and badge counts.
    """
    student_id = request.session.get('student_id')
    if not student_id:
        s_param = request.GET.get('id')
        if s_param and s_param.isdigit():
            student = get_object_or_404(Student, id=int(s_param))
        else:
            messages.info(request, "Please log in to view and print your Certificate of Cyber Mastery.")
            return redirect('student_login')
    else:
        student = get_object_or_404(Student, id=student_id)

    earned_badges = student.get_earned_badges()
    badges_unlocked = sum(1 for b in earned_badges if b['earned'])
    attempts = QuizAttempt.objects.filter(student=student)
    total_quizzes = attempts.count()
    avg_accuracy = student.average_score

    # Unique certificate serial number based on student id and roll
    cert_id = f"CS-CERT-2026-{student.id:04d}-{student.roll_number}"
    issue_date = timezone.now().strftime("%B %d, %Y")

    return render(request, 'quizzes/certificate.html', {
        'student': student,
        'cert_id': cert_id,
        'issue_date': issue_date,
        'rank_title': student.rank_title,
        'badges_unlocked': badges_unlocked,
        'total_quizzes': total_quizzes,
        'avg_accuracy': avg_accuracy,
    })

