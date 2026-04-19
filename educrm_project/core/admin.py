from django.contrib import admin
from .models import Course, Teacher, Student, Group, Enrollment, Attendance, Payment, Notification


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_type', 'price_per_month', 'duration_months', 'is_active']
    list_filter = ['course_type', 'is_active']
    search_fields = ['name']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'salary_rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['first_name', 'last_name', 'phone']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'school', 'grade', 'source', 'status', 'registered_at']
    list_filter = ['status', 'source']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    date_hierarchy = 'registered_at'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'teacher', 'schedule', 'status', 'start_date']
    list_filter = ['status', 'course']
    search_fields = ['name']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'status', 'enrolled_date', 'discount_percent']
    list_filter = ['status']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'date', 'status']
    list_filter = ['status', 'date']
    date_hierarchy = 'date'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'payment_type', 'method', 'status', 'payment_date']
    list_filter = ['status', 'payment_type', 'method']
    date_hierarchy = 'payment_date'
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['student', 'notification_type', 'is_sent', 'created_at']
    list_filter = ['notification_type', 'is_sent']
