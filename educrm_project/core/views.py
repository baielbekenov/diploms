from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import date, timedelta
from .models import Student, Teacher, Course, Group, Enrollment, Attendance, Payment
from .forms import (StudentForm, TeacherForm, CourseForm, GroupForm,
                    EnrollmentForm, AttendanceBulkForm, PaymentForm, StudentSearchForm)


@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    stats = {
        'total_students': Student.objects.filter(status='active').count(),
        'total_groups': Group.objects.filter(status='active').count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        'monthly_revenue': Payment.objects.filter(
            status='confirmed',
            payment_date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'new_students_month': Student.objects.filter(
            registered_at__date__gte=month_start
        ).count(),
        'pending_payments': Payment.objects.filter(status='pending').count(),
    }

    recent_payments = Payment.objects.filter(status='confirmed').select_related('student').order_by('-created_at')[:5]
    recent_students = Student.objects.order_by('-registered_at')[:5]
    active_groups = Group.objects.filter(status='active').select_related('course', 'teacher')[:6]

    # Revenue by month (last 6 months)
    revenue_data = []
    for i in range(5, -1, -1):
        m = today.replace(day=1) - timedelta(days=i * 30)
        m_start = m.replace(day=1)
        if m.month == 12:
            m_end = m.replace(year=m.year + 1, month=1, day=1)
        else:
            m_end = m.replace(month=m.month + 1, day=1)
        total = Payment.objects.filter(
            status='confirmed',
            payment_date__gte=m_start,
            payment_date__lt=m_end
        ).aggregate(t=Sum('amount'))['t'] or 0
        months_ru = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
                     'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
        revenue_data.append({'month': months_ru[m_start.month - 1], 'amount': float(total)})

    context = {
        'stats': stats,
        'recent_payments': recent_payments,
        'recent_students': recent_students,
        'active_groups': active_groups,
        'revenue_data': revenue_data,
        'today': today,
    }
    return render(request, 'dashboard.html', context)


# ─────────────── STUDENTS ───────────────

@login_required
def student_list(request):
    form = StudentSearchForm(request.GET)
    students = Student.objects.all()

    if form.is_valid():
        q = form.cleaned_data.get('query')
        status = form.cleaned_data.get('status')
        source = form.cleaned_data.get('source')
        if q:
            students = students.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(phone__icontains=q) |
                Q(email__icontains=q)
            )
        if status:
            students = students.filter(status=status)
        if source:
            students = students.filter(source=source)

    students = students.order_by('last_name', 'first_name')
    return render(request, 'students/list.html', {'students': students, 'form': form})


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.select_related('group__course', 'group__teacher').all()
    payments = student.payments.all()[:10]
    return render(request, 'students/detail.html', {
        'student': student,
        'enrollments': enrollments,
        'payments': payments,
    })


@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Студент {student.full_name} успешно добавлен.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm()
    return render(request, 'students/form.html', {'form': form, 'title': 'Добавить студента'})


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные студента обновлены.')
            return redirect('student_detail', pk=pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/form.html', {
        'form': form, 'student': student, 'title': 'Редактировать студента'
    })


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.full_name
        student.delete()
        messages.success(request, f'Студент {name} удалён.')
        return redirect('student_list')
    return render(request, 'confirm_delete.html', {'object': student, 'back_url': 'student_list'})


# ─────────────── TEACHERS ───────────────

@login_required
def teacher_list(request):
    teachers = Teacher.objects.filter(is_active=True).prefetch_related('courses')
    return render(request, 'teachers/list.html', {'teachers': teachers})


@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    groups = teacher.groups.select_related('course').all()
    return render(request, 'teachers/detail.html', {'teacher': teacher, 'groups': groups})


@login_required
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f'Учитель {teacher.full_name} добавлен.')
            return redirect('teacher_detail', pk=teacher.pk)
    else:
        form = TeacherForm()
    return render(request, 'teachers/form.html', {'form': form, 'title': 'Добавить учителя'})


@login_required
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные учителя обновлены.')
            return redirect('teacher_detail', pk=pk)
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'teachers/form.html', {
        'form': form, 'teacher': teacher, 'title': 'Редактировать учителя'
    })


# ─────────────── COURSES ───────────────

@login_required
def course_list(request):
    courses = Course.objects.annotate(group_count=Count('groups')).all()
    return render(request, 'courses/list.html', {'courses': courses})


@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Курс «{course.name}» создан.')
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/form.html', {'form': form, 'title': 'Создать курс'})


@login_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс обновлён.')
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/form.html', {'form': form, 'course': course, 'title': 'Редактировать курс'})


# ─────────────── GROUPS ───────────────

@login_required
def group_list(request):
    groups = Group.objects.select_related('course', 'teacher').annotate(
        enrolled_count=Count('enrollments', filter=Q(enrollments__status='active'))
    ).all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        groups = groups.filter(status=status_filter)
    return render(request, 'groups/list.html', {'groups': groups, 'status_filter': status_filter})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    enrollments = group.enrollments.filter(status='active').select_related('student')
    recent_attendance = Attendance.objects.filter(
        enrollment__group=group
    ).select_related('enrollment__student').order_by('-date')[:30]

    # Attendance by date
    dates = sorted(set(a.date for a in recent_attendance), reverse=True)[:10]

    return render(request, 'groups/detail.html', {
        'group': group,
        'enrollments': enrollments,
        'recent_attendance': recent_attendance,
        'dates': dates,
    })


@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Группа «{group.name}» создана.')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupForm()
    return render(request, 'groups/form.html', {'form': form, 'title': 'Создать группу'})


@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа обновлена.')
            return redirect('group_detail', pk=pk)
    else:
        form = GroupForm(instance=group)
    return render(request, 'groups/form.html', {
        'form': form, 'group': group, 'title': 'Редактировать группу'
    })


# ─────────────── ENROLLMENT ───────────────

@login_required
def enrollment_create(request, student_pk=None, group_pk=None):
    initial = {}
    if student_pk:
        student = get_object_or_404(Student, pk=student_pk)
        initial['student'] = student
    if group_pk:
        group = get_object_or_404(Group, pk=group_pk)
        initial['group'] = group

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, f'{enrollment.student.full_name} зачислен в {enrollment.group.name}.')
            return redirect('group_detail', pk=enrollment.group.pk)
    else:
        form = EnrollmentForm(initial=initial)
    return render(request, 'enrollment_form.html', {'form': form})


@login_required
def enrollment_update_status(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Enrollment.STATUS_CHOICES):
        enrollment.status = new_status
        if new_status in ['completed', 'dropped']:
            enrollment.completion_date = timezone.now().date()
        enrollment.save()
        messages.success(request, f'Статус зачисления изменён на «{enrollment.get_status_display()}».')
    return redirect('group_detail', pk=enrollment.group.pk)


# ─────────────── ATTENDANCE ───────────────

@login_required
def attendance_mark(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk)
    enrollments = group.enrollments.filter(status='active').select_related('student')

    if request.method == 'POST':
        date_str = request.POST.get('date')
        try:
            att_date = date.fromisoformat(date_str)
        except (ValueError, TypeError):
            messages.error(request, 'Некорректная дата.')
            return redirect('attendance_mark', group_pk=group_pk)

        for enrollment in enrollments:
            status = request.POST.get(f'status_{enrollment.pk}', 'absent')
            notes = request.POST.get(f'notes_{enrollment.pk}', '')
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=att_date,
                defaults={'status': status, 'notes': notes, 'marked_by': request.user}
            )
        messages.success(request, f'Посещаемость за {att_date.strftime("%d.%m.%Y")} сохранена.')
        return redirect('group_detail', pk=group_pk)

    today = timezone.now().date()
    # Pre-load existing attendance for today
    existing = {}
    for a in Attendance.objects.filter(enrollment__group=group, date=today):
        existing[a.enrollment_id] = a

    return render(request, 'attendance/mark.html', {
        'group': group,
        'enrollments': enrollments,
        'today': today,
        'existing': existing,
        'status_choices': Attendance.STATUS_CHOICES,
    })


@login_required
def attendance_history(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk)
    records = Attendance.objects.filter(
        enrollment__group=group
    ).select_related('enrollment__student').order_by('-date')

    date_filter = request.GET.get('date')
    if date_filter:
        records = records.filter(date=date_filter)

    return render(request, 'attendance/history.html', {
        'group': group,
        'records': records,
        'date_filter': date_filter,
    })


# ─────────────── PAYMENTS ───────────────

@login_required
def payment_list(request):
    payments = Payment.objects.select_related('student', 'enrollment__group').order_by('-payment_date')
    month = request.GET.get('month')
    if month:
        try:
            m = date.fromisoformat(month + '-01')
            payments = payments.filter(
                payment_date__year=m.year,
                payment_date__month=m.month
            )
        except ValueError:
            pass

    total = payments.filter(status='confirmed').aggregate(t=Sum('amount'))['t'] or 0
    return render(request, 'payments/list.html', {
        'payments': payments,
        'total': total,
        'month': month,
    })


@login_required
def payment_create(request, student_pk=None):
    student = get_object_or_404(Student, pk=student_pk) if student_pk else None
    if request.method == 'POST':
        form = PaymentForm(request.POST, student=student)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.recorded_by = request.user
            payment.save()
            messages.success(request, f'Платёж {payment.amount} сом записан.')
            if student_pk:
                return redirect('student_detail', pk=student_pk)
            return redirect('payment_list')
    else:
        form = PaymentForm(student=student)
    return render(request, 'payments/form.html', {'form': form, 'student': student})


@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    student_pk = payment.student.pk
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Платёж удалён.')
        return redirect('student_detail', pk=student_pk)
    return render(request, 'confirm_delete.html', {
        'object': payment,
        'back_url': 'student_detail',
        'back_pk': student_pk
    })


# ─────────────── REPORTS ───────────────

@login_required
def report_overview(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Students by source
    by_source = Student.objects.values('source').annotate(count=Count('id'))
    source_labels = {k: v for k, v in Student.SOURCE_CHOICES}
    source_data = [{'label': source_labels.get(s['source'], s['source']), 'count': s['count']} for s in by_source]

    # Payments by method this month
    by_method = Payment.objects.filter(
        status='confirmed', payment_date__gte=month_start
    ).values('method').annotate(total=Sum('amount'))

    # Low attendance students (< 70%)
    low_attendance = []
    for enrollment in Enrollment.objects.filter(status='active').select_related('student', 'group'):
        rate = enrollment.attendance_rate()
        if rate is not None and rate < 70:
            low_attendance.append({'enrollment': enrollment, 'rate': rate})
    low_attendance.sort(key=lambda x: x['rate'])

    # Debt students
    debtors = [s for s in Student.objects.filter(status='active') if s.total_debt() > 0]

    context = {
        'source_data': source_data,
        'by_method': list(by_method),
        'low_attendance': low_attendance[:10],
        'debtors': debtors[:10],
        'today': today,
    }
    return render(request, 'reports/overview.html', context)
