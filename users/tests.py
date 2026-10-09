from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()


class StudentAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_student_model_creation(self):
        student = Student.objects.create(name="Alex Smith", class_name="Grade 8-A", roll_number="42")
        self.assertEqual(str(student), "Alex Smith (Grade 8-A - #42)")
        self.assertEqual(student.total_attempts, 0)
        self.assertEqual(student.average_score, 0.0)

    def test_student_frictionless_login(self):
        response = self.client.post('/student/login/', {
            'name': 'Jordan Lee',
            'class_name': 'Grade 9-B',
            'roll_number': '15',
        }, follow=True)
        self.assertRedirects(response, '/dashboard/')
        
        # Verify student exists in DB
        student = Student.objects.get(class_name='Grade 9-B', roll_number='15')
        self.assertEqual(student.name, 'Jordan Lee')
        
        # Verify session has student_id
        session = self.client.session
        self.assertEqual(session.get('student_id'), student.id)

    def test_student_logout(self):
        # First log in
        self.client.post('/student/login/', {
            'name': 'Sam Doe',
            'class_name': 'Grade 10-A',
            'roll_number': '09',
        })
        self.assertTrue('student_id' in self.client.session)

        # Logout
        response = self.client.get('/student/logout/', follow=True)
        self.assertRedirects(response, '/')
        self.assertNotIn('student_id', self.client.session)


class TeacherAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='ms_carter',
            password='TestPassword123!',
            is_staff=True
        )

    def test_teacher_valid_login(self):
        response = self.client.post('/teacher/login/', {
            'username': 'ms_carter',
            'password': 'TestPassword123!',
        }, follow=True)
        self.assertRedirects(response, '/teacher/dashboard/')
        self.assertTrue(response.context['user'].is_authenticated)

    def test_teacher_invalid_login(self):
        response = self.client.post('/teacher/login/', {
            'username': 'ms_carter',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_teacher_logout(self):
        self.client.login(username='ms_carter', password='TestPassword123!')
        response = self.client.get('/teacher/logout/', follow=True)
        self.assertRedirects(response, '/')
