FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

COPY . .

RUN python3.11 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

RUN pip install --upgrade pip && pip install -r requirements.txt
RUN python manage.py migrate

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "kittygram.wsgi:application"]