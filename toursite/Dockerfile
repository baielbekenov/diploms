# Базовый образ
FROM python:3.12-slim

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем проект
COPY . .

# Собираем статику (если используешь)
RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE 5000

# Команда запуска
CMD ["gunicorn", "main.wsgi:application", "--bind", "0.0.0.0:5000"]