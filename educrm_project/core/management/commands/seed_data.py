from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random
from core.models import Course, Teacher, Student, Group, Enrollment, Attendance, Payment


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('Создание демо-данных...')

        # Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@educrm.kg', 'admin123')
            self.stdout.write(self.style.SUCCESS('Создан admin/admin123'))

        # Courses
        courses_data = [
            {'name': 'Подготовка к ОРТ (полный)', 'course_type': 'ort', 'price_per_month': 4500, 'duration_months': 6},
            {'name': 'Подготовка к ОРТ (математика)', 'course_type': 'ort', 'price_per_month': 2500, 'duration_months': 4},
            {'name': 'Английский язык — Beginner', 'course_type': 'language', 'language': 'en', 'price_per_month': 3000, 'duration_months': 6},
            {'name': 'Английский язык — Intermediate', 'course_type': 'language', 'language': 'en', 'price_per_month': 3500, 'duration_months': 6},
            {'name': 'Турецкий язык', 'course_type': 'language', 'language': 'tr', 'price_per_month': 2800, 'duration_months': 8},
            {'name': 'Китайский язык', 'course_type': 'language', 'language': 'cn', 'price_per_month': 3200, 'duration_months': 12},
        ]
        courses = []
        for cd in courses_data:
            c, _ = Course.objects.get_or_create(name=cd['name'], defaults=cd)
            courses.append(c)
        self.stdout.write(f'  {len(courses)} курсов')

        # Teachers
        teachers_data = [
            {'first_name': 'Айгуль', 'last_name': 'Маматова', 'phone': '+996700111001', 'salary_rate': 350},
            {'first_name': 'Бакыт', 'last_name': 'Токтосунов', 'phone': '+996700111002', 'salary_rate': 400},
            {'first_name': 'Sarah', 'last_name': 'Johnson', 'phone': '+996700111003', 'salary_rate': 600},
            {'first_name': 'Эрлан', 'last_name': 'Асанов', 'phone': '+996700111004', 'salary_rate': 320},
        ]
        teachers = []
        for td in teachers_data:
            t, _ = Teacher.objects.get_or_create(phone=td['phone'], defaults=td)
            teachers.append(t)
        teachers[0].courses.set(courses[:2])
        teachers[1].courses.set(courses[:2])
        teachers[2].courses.set(courses[2:4])
        teachers[3].courses.set(courses[4:])
        self.stdout.write(f'  {len(teachers)} учителей')

        # Students
        first_names = ['Айдай', 'Нурзат', 'Алтынай', 'Жылдыз', 'Гүлзат', 'Мирлан', 'Эрлан', 'Бекзат', 'Канат', 'Улан',
                       'Асель', 'Зарина', 'Диана', 'Айгерим', 'Малика', 'Темир', 'Данияр', 'Руслан', 'Омурбек', 'Нурбек']
        last_names = ['Исаков', 'Алиев', 'Бакытов', 'Султанов', 'Токтоматов', 'Кадыров', 'Усупов', 'Жумалиев',
                      'Мамытов', 'Нурланов', 'Асанова', 'Болотова', 'Карыбекова', 'Тентимишева', 'Орозова']
        schools = ['Школа №1', 'Школа №5', 'Школа №22', 'Лицей №61', 'Гимназия №24', 'Школа №48']
        sources = ['instagram', 'referral', 'walk_in', 'website', 'other']

        students = []
        for i in range(25):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            phone = f'+99670{random.randint(1000000, 9999999)}'
            if not Student.objects.filter(phone=phone).exists():
                s = Student.objects.create(
                    first_name=fn, last_name=ln, phone=phone,
                    school=random.choice(schools),
                    grade=str(random.randint(9, 11)),
                    source=random.choice(sources),
                    status='active',
                    registered_at=timezone.now() - timedelta(days=random.randint(0, 120))
                )
                students.append(s)

        self.stdout.write(f'  {len(students)} студентов')

        # Groups
        groups_data = [
            {'name': 'ОРТ-А (утро)', 'course': courses[0], 'teacher': teachers[0], 'schedule': 'MWF', 'status': 'active', 'max_students': 15},
            {'name': 'ОРТ-Б (вечер)', 'course': courses[0], 'teacher': teachers[1], 'schedule': 'TTS', 'status': 'active', 'max_students': 15},
            {'name': 'Математика ОРТ', 'course': courses[1], 'teacher': teachers[0], 'schedule': 'TTS', 'status': 'active', 'max_students': 12},
            {'name': 'English Beginner-1', 'course': courses[2], 'teacher': teachers[2], 'schedule': 'MWF', 'status': 'active', 'max_students': 10},
            {'name': 'English Intermediate', 'course': courses[3], 'teacher': teachers[2], 'schedule': 'TTS', 'status': 'active', 'max_students': 10},
            {'name': 'Турецкий A1', 'course': courses[4], 'teacher': teachers[3], 'schedule': 'SAT_SUN', 'status': 'active', 'max_students': 8},
        ]
        groups = []
        for gd in groups_data:
            g, _ = Group.objects.get_or_create(name=gd['name'], defaults={
                **gd, 'start_date': date.today() - timedelta(days=60)
            })
            groups.append(g)
        self.stdout.write(f'  {len(groups)} групп')

        # Enrollments
        enrollment_count = 0
        for i, s in enumerate(students):
            group = groups[i % len(groups)]
            if not Enrollment.objects.filter(student=s, group=group).exists():
                Enrollment.objects.create(student=s, group=group, status='active',
                                          enrolled_date=date.today() - timedelta(days=random.randint(10, 60)))
                enrollment_count += 1
        self.stdout.write(f'  {enrollment_count} зачислений')

        # Attendance (last 2 weeks)
        att_count = 0
        for enrollment in Enrollment.objects.filter(status='active'):
            for days_ago in range(14, 0, -1):
                if random.random() > 0.2:  # 80% chance of lesson
                    att_date = date.today() - timedelta(days=days_ago)
                    if not Attendance.objects.filter(enrollment=enrollment, date=att_date).exists():
                        status = random.choices(
                            ['present', 'absent', 'late', 'excused'],
                            weights=[75, 15, 7, 3]
                        )[0]
                        Attendance.objects.create(enrollment=enrollment, date=att_date, status=status)
                        att_count += 1
        self.stdout.write(f'  {att_count} записей посещаемости')

        # Payments (last 2 months)
        pay_count = 0
        for enrollment in Enrollment.objects.filter(status='active'):
            for months_ago in [1, 2]:
                if random.random() > 0.15:
                    pay_date = date.today() - timedelta(days=months_ago * 30 + random.randint(-5, 5))
                    method = random.choice(['cash', 'transfer', 'card'])
                    Payment.objects.create(
                        student=enrollment.student,
                        enrollment=enrollment,
                        amount=enrollment.effective_price,
                        payment_type='monthly',
                        method=method,
                        status='confirmed',
                        payment_date=pay_date,
                    )
                    pay_count += 1
        self.stdout.write(f'  {pay_count} платежей')

        self.stdout.write(self.style.SUCCESS('\n✓ Демо-данные успешно созданы!'))
        self.stdout.write(self.style.SUCCESS('  Войдите: admin / admin123'))
