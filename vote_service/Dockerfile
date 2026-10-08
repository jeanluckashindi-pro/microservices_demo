# ============================================================
# VOTE SERVICE - Dockerfile
# ============================================================
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["gunicorn", "vote_service.wsgi:application", "--bind", "0.0.0.0:8001"]
