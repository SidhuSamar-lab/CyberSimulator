from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import Student
from .forms import StudentLoginForm, StudentSignUpForm, TeacherLoginForm, TeacherSignUpForm

User = get_user_model()


@never_cache
def student_login(request):
    """
    Handles secure student login via verified email and password.
    """
    # If already logged in as a student, redirect to dashboard
    if request.session.get('student_id'):
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']

            student = Student.objects.filter(email__iexact=email).first()
            if student and student.check_password(password):
                # Set student in session
                request.session['student_id'] = student.id
                request.session['student_name'] = student.name
                messages.success(request, f"Welcome back, Cadet {student.name}!")
                response = redirect('student_dashboard')
                response.set_cookie('cybershield_cadet_id', str(student.id), max_age=86400 * 30, samesite='Lax')
                return response
            else:
                messages.error(request, "Invalid email or password. Please verify your credentials or register.")
    else:
        form = StudentLoginForm()

    return render(request, 'users/student_login.html', {'form': form})


@never_cache
def student_signup(request):
    """
    Handles student registration with Name, Class, Roll Number, Email, and Password.
    """
    if request.session.get('student_id'):
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            class_name = form.cleaned_data['class_name'].strip()
            roll_number = form.cleaned_data['roll_number'].strip()
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']

            # Check if student record exists without email/password (e.g. from existing roster)
            student = Student.objects.filter(roll_number=roll_number, class_name=class_name).first()
            if student and not student.email:
                student.name = name
                student.email = email
                student.set_password(password)
                student.save()
            else:
                student = Student.objects.create(
                    name=name,
                    class_name=class_name,
                    roll_number=roll_number,
                    email=email,
                )
                student.set_password(password)
                student.save()

            # Set student in session
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            messages.success(request, f"Welcome to CyberShield, Cadet {student.name}! Your account is active.")
            response = redirect('student_dashboard')
            response.set_cookie('cybershield_cadet_id', str(student.id), max_age=86400 * 30, samesite='Lax')
            return response
    else:
        form = StudentSignUpForm()

    return render(request, 'users/student_signup.html', {'form': form})


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
    Secure username/email and password login for verified faculty educators.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email'].strip()
            password = form.cleaned_data['password']

            username = username_or_email
            if '@' in username_or_email:
                user_match = User.objects.filter(email__iexact=username_or_email).first()
                if user_match:
                    username = user_match.username

            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                next_url = request.GET.get('next') or 'teacher_dashboard'
                return redirect(next_url)
            else:
                messages.error(request, "Invalid faculty credentials. Please verify your username/email and password.")
    else:
        form = TeacherLoginForm()

    return render(request, 'users/teacher_login.html', {'form': form})


@never_cache
def teacher_signup(request):
    """
    Secure teacher registration with mandatory School Authorization Code verification.
    Prevents unauthorized students from creating faculty accounts.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            email = form.cleaned_data['email'].strip().lower()
            username = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            parts = name.split(None, 1)
            first_name = parts[0] if parts else name
            last_name = parts[1] if len(parts) > 1 else ""

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,
            )

            auth_login(request, user)
            messages.success(request, f"Faculty registration verified! Welcome, {user.get_full_name() or user.username}.")
            return redirect('teacher_dashboard')
    else:
        form = TeacherSignUpForm()

    return render(request, 'users/teacher_signup.html', {'form': form})


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
