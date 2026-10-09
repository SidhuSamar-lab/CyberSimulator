from django import forms
from .models import Student


class StudentLoginForm(forms.Form):
    """
    Frictionless student login form requiring only Name, Class, and Roll Number.
    """
    name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Alex Morgan',
            'class': 'w-full px-4 py-3 rounded-xl bg-slate-900/60 border border-slate-700 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 text-white placeholder-slate-500 transition-all outline-none',
            'autocomplete': 'name',
            'id': 'student_name_input',
        }),
        label="Student Name"
    )
    class_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Grade 9-B',
            'class': 'w-full px-4 py-3 rounded-xl bg-slate-900/60 border border-slate-700 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 text-white placeholder-slate-500 transition-all outline-none',
            'autocomplete': 'off',
            'id': 'class_name_input',
        }),
        label="Class / Grade / Section"
    )
    roll_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. 18 or CS-04',
            'class': 'w-full px-4 py-3 rounded-xl bg-slate-900/60 border border-slate-700 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 text-white placeholder-slate-500 transition-all outline-none',
            'autocomplete': 'off',
            'id': 'roll_number_input',
        }),
        label="Roll Number / ID"
    )
