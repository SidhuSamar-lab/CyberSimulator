from .models import Student


def current_student(request):
    """
    Injects the active logged-in Student into templates if a student session exists.
    """
    student_id = request.session.get('student_id')
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            return {'current_student': student}
        except Student.DoesNotExist:
            request.session.pop('student_id', None)
    return {'current_student': None}
