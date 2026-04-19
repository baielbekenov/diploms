from django import forms
from .models import Student, Teacher, Course, Group, Enrollment, Attendance, Payment


def _apply_attrs(form):
    """Inject dark-theme CSS classes into every widget."""
    for field in form.fields.values():
        w = field.widget
        cls = w.__class__.__name__
        if cls in ('TextInput', 'EmailInput', 'NumberInput', 'URLInput',
                   'PasswordInput', 'DateInput', 'TimeInput', 'DateTimeInput'):
            w.attrs.setdefault('class', 'form-control')
        elif cls == 'Textarea':
            w.attrs.setdefault('class', 'form-control')
        elif cls in ('Select',):
            w.attrs.setdefault('class', 'form-select')
        # CheckboxInput, CheckboxSelectMultiple, RadioSelect — leave as-is


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'parent_phone',
                  'email', 'birth_date', 'school', 'grade', 'source', 'status', 'notes']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_attrs(self)


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email',
                  'courses', 'bio', 'salary_rate', 'is_active', 'hired_date']
        widgets = {
            'hired_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
            'courses': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_attrs(self)


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'course_type', 'language', 'description',
                  'duration_months', 'price_per_month', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_attrs(self)


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'course', 'teacher', 'schedule', 'time_start', 'time_end',
                  'room', 'max_students', 'status', 'start_date', 'end_date', 'notes']
        widgets = {
            'time_start': forms.TimeInput(attrs={'type': 'time'}),
            'time_end': forms.TimeInput(attrs={'type': 'time'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_attrs(self)


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'group', 'status', 'enrolled_date', 'discount_percent', 'notes']
        widgets = {
            'enrolled_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_attrs(self)


class AttendanceBulkForm(forms.Form):
    date = forms.DateField(
        label='Дата занятия',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'enrollment', 'payment_type', 'method', 'amount',
                  'status', 'payment_date', 'period_month', 'receipt_number', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'period_month': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_attrs(self)
        if student:
            self.fields['student'].initial = student
            self.fields['enrollment'].queryset = Enrollment.objects.filter(
                student=student, status='active'
            )


class StudentSearchForm(forms.Form):
    query = forms.CharField(
        label='Поиск',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Имя, фамилия, телефон...'})
    )
    status = forms.ChoiceField(
        label='Статус',
        required=False,
        choices=[('', 'Все')] + Student.STATUS_CHOICES
    )
    source = forms.ChoiceField(
        label='Источник',
        required=False,
        choices=[('', 'Все')] + Student.SOURCE_CHOICES
    )
