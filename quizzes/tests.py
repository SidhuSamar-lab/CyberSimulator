from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from users.models import Student
from .models import QuizAttempt, AttemptQuestion
from .topics import CYBER_TOPICS, get_topic_by_id
from .ai_service import ai_client

User = get_user_model()


class QuizzesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            name="Taylor Swift",
            class_name="Grade 11-A",
            roll_number="13"
        )
        self.teacher = User.objects.create_user(
            username="prof_jones",
            password="TeacherPass123!",
            is_staff=True
        )

    def test_topics_catalog(self):
        self.assertEqual(len(CYBER_TOPICS), 8)
        phishing = get_topic_by_id("phishing")
        self.assertIsNotNone(phishing)
        self.assertEqual(phishing["title"], "Phishing Scams")

    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CyberSimulator")
        self.assertContains(response, "Phishing Scams")

    def test_student_dashboard_requires_session(self):
        # Without session, should redirect to login
        response = self.client.get('/dashboard/')
        self.assertRedirects(response, '/student/login/')

        # With session, loads dashboard
        session = self.client.session
        session['student_id'] = self.student.id
        session.save()

        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Taylor Swift")

    def test_quiz_lifecycle_and_submission(self):
        # 1. Log in student
        session = self.client.session
        session['student_id'] = self.student.id
        session.save()

        # 2. Take quiz on phishing
        response = self.client.get('/quiz/phishing/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scenario Challenge")
        self.assertIn('active_quiz', self.client.session)

        # 3. Submit quiz answers
        active_quiz = self.client.session['active_quiz']
        questions = active_quiz['questions']
        self.assertEqual(len(questions), 3)

        # Answer q_1 correctly, q_2 wrong, q_3 correctly
        correct_1 = questions[0]['correct_option']
        wrong_2 = 'A' if questions[1]['correct_option'] != 'A' else 'B'
        correct_3 = questions[2]['correct_option']

        submit_response = self.client.post('/quiz-submit/', {
            'q_1': correct_1,
            'q_2': wrong_2,
            'q_3': correct_3,
        }, follow=True)

        self.assertEqual(submit_response.status_code, 200)

        # Verify QuizAttempt created
        attempt = QuizAttempt.objects.filter(student=self.student).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.score, 2)
        self.assertEqual(attempt.total_questions, 3)
        self.assertEqual(attempt.percentage, 66.7)
        self.assertTrue(len(attempt.ai_feedback) > 0)

        # Verify AttemptQuestions created
        saved_questions = AttemptQuestion.objects.filter(attempt=attempt)
        self.assertEqual(saved_questions.count(), 3)
        self.assertTrue(saved_questions.filter(is_correct=True).count() == 2)
        self.assertTrue(saved_questions.filter(is_correct=False).count() == 1)

    def test_teacher_dashboard_access_control(self):
        # Anonymous user denied
        response = self.client.get('/teacher/dashboard/')
        self.assertRedirects(response, '/teacher/login/?next=/teacher/dashboard/')

        # Staff user permitted
        self.client.login(username='prof_jones', password='TeacherPass123!')
        response = self.client.get('/teacher/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cybersecurity Topic Proficiency")

    def test_teacher_analytics_api(self):
        self.client.login(username='prof_jones', password='TeacherPass123!')
        response = self.client.get('/teacher/api/analytics/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('labels', data)
        self.assertIn('averages', data)
        self.assertEqual(len(data['labels']), 8)
