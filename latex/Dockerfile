# Используем официальный образ Python
FROM python:3.11-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-latex-recommended \
    texlive-latex-extra \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копируем requirements
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# Копируем остальные файлы проекта
COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 3712

# Команда по умолчанию (можно переопределить в docker-compose)
CMD ["gunicorn", "main.wsgi:application", "--bind", "0.0.0.0:3712"]