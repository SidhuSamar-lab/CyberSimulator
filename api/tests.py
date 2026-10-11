"""
CyberSimulator - API v1 Test Suite.
Tests API root discovery, health check, topics list, topic detail, quiz generation, and analytics.
"""
from django.test import TestCase, Client
from users.models import Student
from quizzes.models import QuizAttempt


class ApiV1Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            name="Grace Hopper",
            class_name="Grade 10-A",
            roll_number="101"
        )

    def test_api_root_discovery(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], "CyberSimulator Core API")
        self.assertIn('endpoints', data['data'])

    def test_api_health_check(self):
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], "healthy")
        self.assertTrue(data['data']['database']['connected'])

    def test_api_topics_list(self):
        response = self.client.get('/api/v1/topics/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['count'], 8)
        self.assertEqual(len(data['data']['topics']), 8)

    def test_api_topic_detail_valid(self):
        response = self.client.get('/api/v1/topics/phishing/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], "phishing")

    def test_api_topic_detail_not_found(self):
        response = self.client.get('/api/v1/topics/non_existent_topic/')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], "TOPIC_NOT_FOUND")

    def test_api_quiz_generate(self):
        response = self.client.get('/api/v1/quiz/generate/phishing/?count=3')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['topic_id'], "phishing")
        self.assertEqual(len(data['data']['questions']), 3)

    def test_api_teacher_analytics(self):
        QuizAttempt.objects.create(
            student=self.student,
            topic_id='phishing',
            topic_title='Phishing Scams',
            score=3,
            total_questions=3
        )
        response = self.client.get('/api/v1/teacher/analytics/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['total_students'], 1)
        self.assertEqual(data['data']['total_attempts'], 1)
