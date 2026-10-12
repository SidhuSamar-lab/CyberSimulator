from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import Student
from .forms import StudentLoginForm


@never_cache
def student_login(request):
    """
    Handles frictionless student login.
    No passwords required - creates or fetches student based on roll_number and class_name.
    """
    # If already logged in as a student, redirect to dashboard
    if request.session.get('student_id'):
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            class_name = form.cleaned_data['class_name'].strip()
            roll_number = form.cleaned_data['roll_number'].strip()

            student, created = Student.objects.get_or_create(
                roll_number=roll_number,
                class_name=class_name,
                defaults={'name': name}
            )

            # Update name if student typed a new variation
            if not created and student.name != name:
                student.name = name
                student.save(update_fields=['name'])

            # Set student in session
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            messages.success(request, f"Welcome back, {student.name}!")
            return redirect('student_dashboard')
    else:
        form = StudentLoginForm()

    return render(request, 'users/student_login.html', {'form': form})


@never_cache
def student_logout(request):
    """Clears and flushes student session completely."""
    request.session.flush()
    messages.info(request, "You have exited your student session.")
    response = redirect('home')
    response.delete_cookie('cybershield_cadet_id')
    response.delete_cookie('sessionid')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@never_cache
def teacher_login(request):
    """
    Secure username/password login for teachers and administrators.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next') or 'teacher_dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please check your credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'users/teacher_login.html', {'form': form})


@never_cache
def teacher_logout(request):
    """Logs out the teacher and flushes session completely."""
    auth_logout(request)
    request.session.flush()
    messages.info(request, "You have been logged out of the teacher portal.")
    response = redirect('home')
    response.delete_cookie('cybershield_teacher_token')
    response.delete_cookie('sessionid')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
