FROM python:3.10

# Рабочая директория внутри контейнера
WORKDIR /usr/src/app

# Копируем все файлы проекта
COPY . .

# Устанавливаем зависимости через poetry
RUN pip install --upgrade pip poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root

# Отключаем буферизацию и запись pyc
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Команда по умолчанию
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
