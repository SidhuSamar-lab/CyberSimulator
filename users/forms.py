from django import forms
from django.contrib.auth import get_user_model
from config.env import AppConfig
from .models import Student

User = get_user_model()

INPUT_STYLE = (
    "w-full h-12 px-4 bg-ink-950 border border-white/10 rounded-xl font-body text-sm "
    "text-white placeholder:text-mist-900 focus:outline-none focus:border-signal "
    "focus:ring-1 focus:ring-signal transition-all"
)


class StudentLoginForm(forms.Form):
    """
    Student login form requiring verified Email and Password.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'e.g. alex.morgan@school.edu',
            'class': INPUT_STYLE,
            'autocomplete': 'email',
            'id': 'student_email_input',
        }),
        label="Student Email"
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': INPUT_STYLE,
            'autocomplete': 'current-password',
            'id': 'student_password_input',
        }),
        label="Password"
    )


CLASS_OPTIONS = [
    f"Class {c}-{s}"
    for c in range(6, 13)
    for s in ["A", "B", "C", "D"]
]


class StudentSignUpForm(forms.Form):
    """
    Student registration form requiring Name, Class, Roll Number, Email, and Password.
    """
    name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Alex Morgan',
            'class': INPUT_STYLE,
            'autocomplete': 'name',
            'id': 'student_name_input',
        }),
        label="Full Name"
    )
    class_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.Select(
            choices=[("", "Select Class & Section")] + [(c, c) for c in CLASS_OPTIONS],
            attrs={
                'class': INPUT_STYLE + " cursor-pointer",
                'id': 'class_name_input',
            }
        ),
        label="Class & Section"
    )
    roll_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. 101',
            'class': INPUT_STYLE,
            'autocomplete': 'off',
            'id': 'roll_number_input',
        }),
        label="Roll Number / ID"
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'e.g. alex.morgan@school.edu',
            'class': INPUT_STYLE,
            'autocomplete': 'email',
            'id': 'student_signup_email_input',
        }),
        label="Student Email"
    )
    password = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Min 6 characters',
            'class': INPUT_STYLE,
            'autocomplete': 'new-password',
            'id': 'student_signup_password_input',
        }),
        label="Create Password"
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Re-enter your password',
            'class': INPUT_STYLE,
            'autocomplete': 'new-password',
            'id': 'student_signup_confirm_password_input',
        }),
        label="Confirm Password"
    )

    def clean_class_name(self):
        val = self.cleaned_data.get('class_name', '').strip()
        if val.startswith("Grade "):
            val = "Class " + val[6:]
        if val not in CLASS_OPTIONS:
            raise forms.ValidationError("Please select a valid class from Class 6 to 12 (sections A, B, C, D).")
        return val

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Student.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A student account with this email address already exists. Please sign in.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


class TeacherLoginForm(forms.Form):
    """
    Teacher login form accepting Username or Email, along with Password.
    """
    username_or_email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or Email',
            'class': INPUT_STYLE,
            'autocomplete': 'username',
            'id': 'teacher_user_input',
        }),
        label="Teacher Username or Email"
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': INPUT_STYLE,
            'autocomplete': 'current-password',
            'id': 'teacher_password_input',
        }),
        label="Password"
    )


class TeacherSignUpForm(forms.Form):
    """
    Teacher registration form requiring Name, Email, Username, Password,
    and the MANDATORY School Authorization Code.
    """
    name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Sarah Jenkins',
            'class': INPUT_STYLE,
            'autocomplete': 'name',
            'id': 'teacher_signup_name_input',
        }),
        label="Full Name"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'e.g. s.jenkins@school.edu',
            'class': INPUT_STYLE,
            'autocomplete': 'email',
            'id': 'teacher_signup_email_input',
        }),
        label="Institutional Email"
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. prof_jenkins',
            'class': INPUT_STYLE,
            'autocomplete': 'username',
            'id': 'teacher_signup_username_input',
        }),
        label="Desired Username"
    )
    password = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Min 6 characters',
            'class': INPUT_STYLE,
            'autocomplete': 'new-password',
            'id': 'teacher_signup_pass_input',
        }),
        label="Create Password"
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Re-enter your password',
            'class': INPUT_STYLE,
            'autocomplete': 'new-password',
            'id': 'teacher_signup_confirm_pass_input',
        }),
        label="Confirm Password"
    )
    school_code = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter official school code',
            'class': INPUT_STYLE + " border-emerald/40 focus:border-emerald focus:ring-emerald/20",
            'autocomplete': 'off',
            'id': 'teacher_school_code_input',
        }),
        label="School Authorization Code",
        help_text="Mandatory verification code provided only to official school faculty members."
    )

    def clean_school_code(self):
        code = self.cleaned_data.get('school_code', '').strip()
        expected = AppConfig.TEACHER_SCHOOL_CODE.strip()
        if code.lower() != expected.lower():
            raise forms.ValidationError(
                "Invalid School Authorization Code. Teacher registration is strictly restricted to verified school faculty members."
            )
        return code

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data
