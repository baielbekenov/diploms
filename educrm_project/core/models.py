from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Course(models.Model):
    TYPE_ORT = 'ort'
    TYPE_LANGUAGE = 'language'
    TYPE_OTHER = 'other'
    TYPE_CHOICES = [
        (TYPE_ORT, 'Подготовка к ОРТ'),
        (TYPE_LANGUAGE, 'Языковые курсы'),
        (TYPE_OTHER, 'Другое'),
    ]

    LANG_KG = 'kg'
    LANG_EN = 'en'
    LANG_RU = 'ru'
    LANG_TR = 'tr'
    LANG_CN = 'cn'
    LANG_DE = 'de'
    LANG_CHOICES = [
        (LANG_KG, 'Кыргызский'),
        (LANG_EN, 'Английский'),
        (LANG_RU, 'Русский'),
        (LANG_TR, 'Турецкий'),
        (LANG_CN, 'Китайский'),
        (LANG_DE, 'Немецкий'),
    ]

    name = models.CharField('Название', max_length=200)
    course_type = models.CharField('Тип курса', max_length=20, choices=TYPE_CHOICES, default=TYPE_ORT)
    language = models.CharField('Язык', max_length=5, choices=LANG_CHOICES, blank=True, null=True)
    description = models.TextField('Описание', blank=True)
    duration_months = models.PositiveIntegerField('Длительность (мес.)', default=3)
    price_per_month = models.DecimalField('Цена/месяц (сом)', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['name']

    def __str__(self):
        return self.name


class Teacher(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True)
    courses = models.ManyToManyField(Course, verbose_name='Курсы', blank=True)
    bio = models.TextField('Биография', blank=True)
    salary_rate = models.DecimalField('Ставка (сом/час)', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('Активен', default=True)
    hired_date = models.DateField('Дата найма', default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учителя'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)


class Student(models.Model):
    SOURCE_INSTAGRAM = 'instagram'
    SOURCE_REFERRAL = 'referral'
    SOURCE_WALK_IN = 'walk_in'
    SOURCE_WEBSITE = 'website'
    SOURCE_OTHER = 'other'
    SOURCE_CHOICES = [
        (SOURCE_INSTAGRAM, 'Instagram'),
        (SOURCE_REFERRAL, 'Рекомендация'),
        (SOURCE_WALK_IN, 'Зашёл сам'),
        (SOURCE_WEBSITE, 'Сайт'),
        (SOURCE_OTHER, 'Другое'),
    ]

    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_GRADUATE = 'graduate'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активный'),
        (STATUS_INACTIVE, 'Неактивный'),
        (STATUS_GRADUATE, 'Выпускник'),
    ]

    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    phone = models.CharField('Телефон', max_length=20)
    parent_phone = models.CharField('Телефон родителя', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    school = models.CharField('Школа', max_length=200, blank=True)
    grade = models.CharField('Класс', max_length=10, blank=True)
    source = models.CharField('Источник', max_length=20, choices=SOURCE_CHOICES, default=SOURCE_OTHER)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    notes = models.TextField('Заметки', blank=True)
    registered_at = models.DateTimeField('Дата регистрации', default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)

    @property
    def age(self):
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    def total_paid(self):
        return sum(p.amount for p in self.payments.filter(status='confirmed'))

    def total_debt(self):
        total_charged = sum(
            e.group.course.price_per_month
            for e in self.enrollments.filter(status='active')
        )
        return max(0, total_charged - self.total_paid())


class Group(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_PLANNED = 'planned'
    STATUS_CHOICES = [
        (STATUS_PLANNED, 'Планируется'),
        (STATUS_ACTIVE, 'Активная'),
        (STATUS_COMPLETED, 'Завершена'),
    ]

    SCHEDULE_CHOICES = [
        ('MWF', 'Пн/Ср/Пт'),
        ('TTS', 'Вт/Чт/Сб'),
        ('DAILY', 'Ежедневно'),
        ('SAT_SUN', 'Сб/Вс'),
        ('MON_FRI', 'Пн-Пт'),
    ]

    name = models.CharField('Название группы', max_length=100)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name='Курс', related_name='groups')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='Учитель', related_name='groups')
    students = models.ManyToManyField(Student, through='Enrollment', verbose_name='Студенты')
    schedule = models.CharField('Расписание', max_length=20, choices=SCHEDULE_CHOICES, default='MWF')
    time_start = models.TimeField('Время начала', null=True, blank=True)
    time_end = models.TimeField('Время окончания', null=True, blank=True)
    room = models.CharField('Аудитория', max_length=50, blank=True)
    max_students = models.PositiveIntegerField('Макс. студентов', default=15)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED)
    start_date = models.DateField('Дата начала', null=True, blank=True)
    end_date = models.DateField('Дата окончания', null=True, blank=True)
    notes = models.TextField('Заметки', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.course.name})"

    @property
    def student_count(self):
        return self.enrollments.filter(status='active').count()

    @property
    def is_full(self):
        return self.student_count >= self.max_students

    @property
    def schedule_display(self):
        return self.get_schedule_display()


class Enrollment(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_DROPPED = 'dropped'
    STATUS_FROZEN = 'frozen'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активный'),
        (STATUS_COMPLETED, 'Завершил'),
        (STATUS_DROPPED, 'Отчислен'),
        (STATUS_FROZEN, 'Заморожен'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент',
                                related_name='enrollments')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа',
                              related_name='enrollments')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    enrolled_date = models.DateField('Дата зачисления', default=timezone.now)
    completion_date = models.DateField('Дата завершения', null=True, blank=True)
    discount_percent = models.PositiveIntegerField('Скидка (%)', default=0)
    notes = models.TextField('Заметки', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Зачисление'
        verbose_name_plural = 'Зачисления'
        unique_together = ['student', 'group']

    def __str__(self):
        return f"{self.student} → {self.group}"

    @property
    def effective_price(self):
        base = self.group.course.price_per_month
        if self.discount_percent:
            return base * (1 - self.discount_percent / 100)
        return base

    def attendance_rate(self):
        records = self.attendance_records.all()
        if not records.exists():
            return None
        present = records.filter(status='present').count()
        return round((present / records.count()) * 100)


class Attendance(models.Model):
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_LATE = 'late'
    STATUS_EXCUSED = 'excused'
    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Присутствовал'),
        (STATUS_ABSENT, 'Отсутствовал'),
        (STATUS_LATE, 'Опоздал'),
        (STATUS_EXCUSED, 'Уважительная причина'),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, verbose_name='Зачисление',
                                   related_name='attendance_records')
    date = models.DateField('Дата')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    notes = models.TextField('Заметки', blank=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Отметил')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        ordering = ['-date']
        unique_together = ['enrollment', 'date']

    def __str__(self):
        return f"{self.enrollment.student} — {self.date} — {self.get_status_display()}"


class Payment(models.Model):
    TYPE_MONTHLY = 'monthly'
    TYPE_REGISTRATION = 'registration'
    TYPE_MATERIAL = 'material'
    TYPE_OTHER = 'other'
    TYPE_CHOICES = [
        (TYPE_MONTHLY, 'Ежемесячная оплата'),
        (TYPE_REGISTRATION, 'Регистрационный взнос'),
        (TYPE_MATERIAL, 'Учебные материалы'),
        (TYPE_OTHER, 'Другое'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_CONFIRMED, 'Подтверждён'),
        (STATUS_CANCELLED, 'Отменён'),
    ]

    METHOD_CASH = 'cash'
    METHOD_TRANSFER = 'transfer'
    METHOD_CARD = 'card'
    METHOD_CHOICES = [
        (METHOD_CASH, 'Наличные'),
        (METHOD_TRANSFER, 'Перевод'),
        (METHOD_CARD, 'Карта'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент',
                                related_name='payments')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Зачисление', related_name='payments')
    payment_type = models.CharField('Тип оплаты', max_length=20, choices=TYPE_CHOICES, default=TYPE_MONTHLY)
    method = models.CharField('Способ оплаты', max_length=20, choices=METHOD_CHOICES, default=METHOD_CASH)
    amount = models.DecimalField('Сумма (сом)', max_digits=10, decimal_places=2)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_CONFIRMED)
    payment_date = models.DateField('Дата оплаты', default=timezone.now)
    period_month = models.DateField('Оплачиваемый период', null=True, blank=True)
    receipt_number = models.CharField('Номер квитанции', max_length=50, blank=True)
    notes = models.TextField('Заметки', blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Записал')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.student} — {self.amount} сом — {self.payment_date}"


class Notification(models.Model):
    TYPE_DEBT = 'debt'
    TYPE_ATTENDANCE = 'attendance'
    TYPE_GENERAL = 'general'
    TYPE_CHOICES = [
        (TYPE_DEBT, 'Задолженность'),
        (TYPE_ATTENDANCE, 'Посещаемость'),
        (TYPE_GENERAL, 'Общее'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES)
    message = models.TextField('Сообщение')
    is_sent = models.BooleanField('Отправлено', default=False)
    sent_at = models.DateTimeField('Время отправки', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} — {self.get_notification_type_display()}"
