from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Student
from quizzes.models import QuizAttempt, AttemptQuestion
from quizzes.topics import CYBER_TOPICS
from quizzes.ai_service import FALLBACK_QUESTIONS

User = get_user_model()


class Command(BaseCommand):
    help = "Initializes default teacher account and realistic demo data (students & quiz attempts)"

    def handle(self, *args, **options):
        # 1. Create Teacher Administrator
        teacher_username = "teacher"
        teacher_password = "TeacherPassword123!"
        teacher_email = "teacher@cybersimulator.edu"

        teacher, created = User.objects.get_or_create(
            username=teacher_username,
            defaults={
                "email": teacher_email,
                "first_name": "Sarah",
                "last_name": "Jenkins",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        teacher.set_password(teacher_password)
        teacher.is_staff = True
        teacher.is_superuser = True
        teacher.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created teacher account: {teacher_username} / {teacher_password}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated teacher account: {teacher_username} / {teacher_password}"))

        # 2. Create sample students
        students_data = [
            {"name": "Alex Morgan", "class_name": "Grade 9-A", "roll_number": "101"},
            {"name": "Jordan Lee", "class_name": "Grade 9-A", "roll_number": "102"},
            {"name": "Sam Taylor", "class_name": "Grade 9-A", "roll_number": "103"},
            {"name": "Riley Patel", "class_name": "Grade 9-B", "roll_number": "201"},
            {"name": "Casey Chen", "class_name": "Grade 9-B", "roll_number": "202"},
            {"name": "Morgan Davis", "class_name": "Grade 10-A", "roll_number": "301"},
        ]

        created_students = []
        for s_data in students_data:
            student, _ = Student.objects.get_or_create(
                roll_number=s_data["roll_number"],
                class_name=s_data["class_name"],
                defaults={"name": s_data["name"]}
            )
            created_students.append(student)

        self.stdout.write(self.style.SUCCESS(f"Populated {len(created_students)} students."))

        # 3. Seed sample quiz attempts for demo data
        if QuizAttempt.objects.count() == 0:
            demo_attempts_plan = [
                (created_students[0], "phishing", 3, [True, True, True]),
                (created_students[0], "otp_scams", 2, [True, False, True]),
                (created_students[0], "passwords_2fa", 3, [True, True, True]),
                (created_students[1], "phishing", 2, [True, True, False]),
                (created_students[1], "fake_websites", 1, [False, True, False]),
                (created_students[2], "cyberbullying", 3, [True, True, True]),
                (created_students[2], "social_privacy", 2, [True, False, True]),
                (created_students[3], "qr_scams", 2, [True, True, False]),
                (created_students[3], "ai_misinformation", 1, [False, False, True]),
                (created_students[4], "phishing", 3, [True, True, True]),
                (created_students[4], "otp_scams", 3, [True, True, True]),
                (created_students[5], "passwords_2fa", 2, [True, False, True]),
            ]

            topic_map = {t["id"]: t["title"] for t in CYBER_TOPICS}

            for student, topic_id, score, correctness in demo_attempts_plan:
                topic_title = topic_map.get(topic_id, topic_id.title())
                total = len(correctness)
                
                feedback = (
                    f"🌟 Great job, {student.name}! You scored {score}/{total} on {topic_title}.\n\n"
                    "You demonstrated strong digital awareness while identifying subtle threat cues. "
                    "Remember to always verify sender identities through official channels before sharing sensitive details."
                )

                attempt = QuizAttempt.objects.create(
                    student=student,
                    topic_id=topic_id,
                    topic_title=topic_title,
                    score=score,
                    total_questions=total,
                    ai_feedback=feedback,
                )

                # Add attempt questions from fallback question pool
                q_pool = FALLBACK_QUESTIONS.get(topic_id, [])
                for idx, is_corr in enumerate(correctness, start=1):
                    raw_q = q_pool[idx - 1] if idx - 1 < len(q_pool) else q_pool[0]
                    correct_opt = raw_q.get("correct_option", "A")
                    
                    if is_corr:
                        student_opt = correct_opt
                    else:
                        options = ["A", "B", "C", "D"]
                        options.remove(correct_opt)
                        student_opt = options[0]

                    AttemptQuestion.objects.create(
                        attempt=attempt,
                        question_number=idx,
                        question_text=raw_q.get("question_text", f"Question {idx}"),
                        option_a=raw_q.get("option_a", "Option A"),
                        option_b=raw_q.get("option_b", "Option B"),
                        option_c=raw_q.get("option_c", "Option C"),
                        option_d=raw_q.get("option_d", "Option D"),
                        correct_option=correct_opt,
                        student_selected_option=student_opt,
                        is_correct=is_corr,
                        explanation=raw_q.get("explanation", "Always practice digital caution."),
                    )

            self.stdout.write(self.style.SUCCESS(f"Created {len(demo_attempts_plan)} demo quiz attempts with questions."))

        self.stdout.write(self.style.SUCCESS("All demo data ready!"))
