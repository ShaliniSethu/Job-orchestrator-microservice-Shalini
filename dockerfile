FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app.py /app/app.py

# Non-root user (good DevOps practice)
RUN useradd -m appuser
USER appuser

EXPOSE 8080

# Use gunicorn for production-like serving
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
