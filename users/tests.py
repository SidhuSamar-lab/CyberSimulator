from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from config.env import AppConfig
from .models import Student

User = get_user_model()


class StudentAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            name="Alex Smith",
            class_name="Class 8-A",
            roll_number="42",
            email="alex.smith@school.edu"
        )
        self.student.set_password("SecretPass123!")
        self.student.save()

    def test_student_model_creation_and_password(self):
        self.assertEqual(str(self.student), "Alex Smith (Class 8-A - #42)")
        self.assertEqual(self.student.total_attempts, 0)
        self.assertEqual(self.student.average_score, 0.0)
        self.assertTrue(self.student.check_password("SecretPass123!"))
        self.assertFalse(self.student.check_password("WrongPassword"))

    def test_student_signup_success(self):
        response = self.client.post('/student/signup/', {
            'name': 'Jordan Lee',
            'class_name': 'Class 9-B',
            'roll_number': '15',
            'email': 'jordan.lee@school.edu',
            'password': 'CadetPassword123!',
            'confirm_password': 'CadetPassword123!',
        }, follow=True)
        self.assertRedirects(response, '/dashboard/')

        # Verify student exists in DB with hashed password
        student = Student.objects.get(email='jordan.lee@school.edu')
        self.assertEqual(student.name, 'Jordan Lee')
        self.assertEqual(student.roll_number, '15')
        self.assertEqual(student.class_name, 'Class 9-B')
        self.assertTrue(student.check_password('CadetPassword123!'))

        # Verify session has student_id
        session = self.client.session
        self.assertEqual(session.get('student_id'), student.id)

    def test_student_signup_mismatched_password(self):
        response = self.client.post('/student/signup/', {
            'name': 'Sam Taylor',
            'class_name': 'Class 10-A',
            'roll_number': '99',
            'email': 'sam.taylor@school.edu',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword456!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Student.objects.filter(email='sam.taylor@school.edu').exists())

    def test_student_signup_duplicate_email(self):
        response = self.client.post('/student/signup/', {
            'name': 'Duplicate Person',
            'class_name': 'Class 8-A',
            'roll_number': '77',
            'email': 'alex.smith@school.edu',  # Already belongs to self.student
            'password': 'SomePassword123!',
            'confirm_password': 'SomePassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_student_login_valid(self):
        response = self.client.post('/student/login/', {
            'email': 'alex.smith@school.edu',
            'password': 'SecretPass123!',
        }, follow=True)
        self.assertRedirects(response, '/dashboard/')
        session = self.client.session
        self.assertEqual(session.get('student_id'), self.student.id)

    def test_student_login_invalid_password(self):
        response = self.client.post('/student/login/', {
            'email': 'alex.smith@school.edu',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertNotIn('student_id', session)

    def test_student_logout(self):
        # First log in
        self.client.post('/student/login/', {
            'email': 'alex.smith@school.edu',
            'password': 'SecretPass123!',
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
            email='ms.carter@school.edu',
            password='TestPassword123!',
            is_staff=True
        )

    def test_teacher_valid_login_with_username(self):
        response = self.client.post('/teacher/login/', {
            'username_or_email': 'ms_carter',
            'password': 'TestPassword123!',
        }, follow=True)
        self.assertRedirects(response, '/teacher/dashboard/')
        self.assertTrue(response.context['user'].is_authenticated)

    def test_teacher_valid_login_with_email(self):
        response = self.client.post('/teacher/login/', {
            'username_or_email': 'ms.carter@school.edu',
            'password': 'TestPassword123!',
        }, follow=True)
        self.assertRedirects(response, '/teacher/dashboard/')
        self.assertTrue(response.context['user'].is_authenticated)

    def test_teacher_invalid_login(self):
        response = self.client.post('/teacher/login/', {
            'username_or_email': 'ms_carter',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_teacher_signup_with_valid_school_code(self):
        response = self.client.post('/teacher/signup/', {
            'name': 'Professor Xavier',
            'email': 'x.professor@school.edu',
            'username': 'prof_x',
            'password': 'FacultyPassword123!',
            'confirm_password': 'FacultyPassword123!',
            'school_code': AppConfig.TEACHER_SCHOOL_CODE,
        }, follow=True)
        self.assertRedirects(response, '/teacher/dashboard/')

        new_teacher = User.objects.get(username='prof_x')
        self.assertTrue(new_teacher.is_staff)
        self.assertTrue(new_teacher.check_password('FacultyPassword123!'))
        self.assertEqual(new_teacher.email, 'x.professor@school.edu')

    def test_teacher_signup_rejected_with_invalid_school_code(self):
        """Ensures students cannot register as teachers without the secret school code."""
        response = self.client.post('/teacher/signup/', {
            'name': 'Sneaky Student',
            'email': 'student@school.edu',
            'username': 'sneaky_student',
            'password': 'StudentPassword123!',
            'confirm_password': 'StudentPassword123!',
            'school_code': 'WRONG-CODE-1234',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid School Authorization Code")
        self.assertFalse(User.objects.filter(username='sneaky_student').exists())

    def test_teacher_logout(self):
        self.client.login(username='ms_carter', password='TestPassword123!')
        response = self.client.get('/teacher/logout/', follow=True)
        self.assertRedirects(response, '/')
